import secrets
import uuid

import jwt
from flask_jwt_extended import create_access_token, create_refresh_token

from src.repositories.user_repository import UserRepository
from src.repositories.role_repository import RoleRepository
from src.models.user_model import User
from src.exceptions.auth_exceptions import ResourceConflictError, InvalidCredentialsError
from src.services.security_service import SecurityService
import requests
import logging

logger = logging.getLogger(__name__)


_DEFAULT_ROLE_NAME = "user"


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def register(self, email: str, password: str) -> dict:
        if self.user_repo.get_by_email(email):
            raise ResourceConflictError("User with this email already exists.")

        role = self.role_repo.get_by_name(_DEFAULT_ROLE_NAME)
        if role is None:
            role = self.role_repo.create(role=_DEFAULT_ROLE_NAME)
            self.user_repo.session.flush()

        password_hash = SecurityService.hash_password(password)
        user = self.user_repo.create(
            email=email,
            hashed_password=password_hash,
            role_id=role.id,
        )
        self.user_repo.session.flush()

        # Create profile in loyalty service
        try:
            from flask import current_app
            loyalty_url = current_app.config.get("LOYALTY_SERVICE_URL")
            if loyalty_url:
                resp = requests.post(
                    f"{loyalty_url}/internal/profile",
                    json={"uuid": str(user.id)},
                    timeout=5
                )
                if not resp.ok:
                    logger.error(f"Failed to create loyalty profile: {resp.text}")
            else:
                logger.warning("LOYALTY_SERVICE_URL not configured, skipping profile creation")
        except Exception as e:
            logger.error(f"Error calling loyalty service: {e}")

        return self._issue_tokens(user)

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password.")

        if not SecurityService.check_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password.")

        return self._issue_tokens(user)

    def refresh(self, incoming_refresh_token: str, jwt_secret: str) -> dict:
        try:
            payload = jwt.decode(
                incoming_refresh_token,
                jwt_secret,
                algorithms=["HS256"],
            )
        except jwt.PyJWTError:
            raise InvalidCredentialsError("Invalid or expired refresh token.")

        try:
            identity_str = str(payload["sub"])
        except KeyError:
            raise InvalidCredentialsError("Invalid or expired refresh token.")
        try:
            uid = uuid.UUID(identity_str)
        except ValueError:
            raise InvalidCredentialsError("Invalid or expired refresh token.")

        user = self.user_repo.get_by_id(uid)
        if user is None or not user.is_active or user.refresh_jwt is None:
            raise InvalidCredentialsError("Invalid or expired refresh token.")
        if len(user.refresh_jwt) != len(incoming_refresh_token):
            raise InvalidCredentialsError("Invalid or expired refresh token.")
        if not secrets.compare_digest(
            user.refresh_jwt,
            incoming_refresh_token,
        ):
            raise InvalidCredentialsError("Invalid or expired refresh token.")

        return self._issue_tokens(user)

    def _issue_tokens(self, user: User) -> dict:
        identity = str(user.id)
        access_plain = create_access_token(identity=identity)
        refresh_plain = create_refresh_token(identity=identity)
        self.user_repo.update(
            user,
            access_jwt=access_plain,
            refresh_jwt=refresh_plain,
        )
        return {
            "access_token": access_plain,
            "refresh_token": refresh_plain,
            "token_type": "bearer",
        }
