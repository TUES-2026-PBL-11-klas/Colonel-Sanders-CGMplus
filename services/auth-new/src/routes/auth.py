from flask_smorest import Blueprint
from flask.views import MethodView
from flask import abort

from src.extensions import db
from src.repositories.user_repository import UserRepository
from src.repositories.role_repository import RoleRepository
from src.services.auth_service import AuthService
from src.exceptions.auth_exceptions import (
    ResourceConflictError,
    InvalidCredentialsError,
)
from src.schemas.token_schema import TokenResponseSchema
from src.schemas.login_schema import LoginSchema
from src.schemas.register_schema import RegisterSchema

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
            return _auth_service().login(
                email=json_data["email"],
                password=json_data["password"],
            )
        except InvalidCredentialsError as e:
            abort(401, description=str(e))
