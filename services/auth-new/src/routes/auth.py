from flask_smorest import Blueprint
from flask.views import MethodView
from flask import abort, current_app
import requests

from src.extensions import db
from src.repositories.user_repository import UserRepository
from src.repositories.role_repository import RoleRepository
from src.services.auth_service import AuthService
from src.exceptions.auth_exceptions import (
    ResourceConflictError,
    InvalidCredentialsError,
)
from src.schemas.auth_schema import (LoginSchema,
    RegisterSchema,
    TokenRefreshSchema,
    TokenResponseSchema
)

blp = Blueprint("auth", "auth", url_prefix="/auth")


def _auth_service() -> AuthService:
    session = db.session
    return AuthService(UserRepository(session), RoleRepository(session))


@blp.route("/register")
class Register(MethodView):
    @blp.arguments(RegisterSchema)
    @blp.response(201, TokenResponseSchema)
    def post(self, json_data):
        try:
            result = _auth_service().register(
                email=json_data["email"],
                password=json_data["password"],
            )
            db.session.commit()

            # Fetch user to get UUID for loyalty service
            user = UserRepository(db.session).get_by_email(json_data["email"])
            if user:
                # Make request to loyalty service
                loyalty_service_url = current_app.config.get("LOYALTY_SERVICE_URL")
                try:
                    requests.post(
                        f"{loyalty_service_url}/internal/profile",
                        json={"uuid": str(user.id)},
                        timeout=5
                    )
                except Exception as e:
                    current_app.logger.error(f"Failed to call loyalty service: {str(e)}")

            return result
        except ResourceConflictError as e:
            db.session.rollback()
            abort(409, description=str(e))


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    @blp.response(200, TokenResponseSchema)
    def post(self, json_data):
        try:
            result = _auth_service().login(
                email=json_data["email"],
                password=json_data["password"],
            )
            db.session.commit()
            return result
        except InvalidCredentialsError as e:
            db.session.rollback()
            abort(401, description=str(e))


@blp.route("/refresh")
class Refresh(MethodView):
    @blp.arguments(TokenRefreshSchema)
    @blp.response(200, TokenResponseSchema)
    def post(self, json_data):
        try:
            result = _auth_service().refresh(
                json_data["refresh_token"],
                current_app.config["JWT_SECRET_KEY"],
            )
            db.session.commit()
            return result
        except InvalidCredentialsError as e:
            db.session.rollback()
            abort(401, description=str(e))
