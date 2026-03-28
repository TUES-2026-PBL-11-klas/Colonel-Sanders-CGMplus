import uuid

from flask_jwt_extended import create_access_token, create_refresh_token

from src.repositories.user_repository import UserRepository
from src.repositories.role_repository import RoleRepository
from src.models.user_model import User
from src.exceptions.auth_exceptions import ResourceConflictError, InvalidCredentialsError
from src.services.security_service import SecurityService


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
        return self._issue_tokens(user)

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password.")

        if not SecurityService.check_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password.")

        return self._issue_tokens(user)

    def refresh(self, identity: str) -> dict:
        uid = uuid.UUID(identity)
        refresh_plain = create_refresh_token(identity=identity)
        self.refresh_token_repo.persist_issued(uid, refresh_plain)
        return {
            "access_token": create_access_token(identity=identity),
            "refresh_token": refresh_plain,
            "token_type": "bearer",
        }

    def _issue_tokens(self, user: User) -> dict:
        identity = str(user.id)
        refresh_plain = create_refresh_token(identity=identity)
        return {
            "access_token": create_access_token(identity=identity),
            "refresh_token": refresh_plain,
            "token_type": "bearer",
        }
