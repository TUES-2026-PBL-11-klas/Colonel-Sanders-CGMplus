import uuid

from flask import abort
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from src.extensions import db
from src.repositories.user_repository import UserRepository
from src.schemas.user_schema import PasswordChangeSchema, UserMeResponseSchema
from src.services.security_service import SecurityService

blp = Blueprint("users", "users", description="User management endpoints.")


@blp.route("/me")
class UserView(MethodView):
    @blp.response(200, UserMeResponseSchema)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def get(self):
        try:
            user_id = uuid.UUID(str(get_jwt_identity()))
        except ValueError:
            abort(400, description="Invalid subject in token.")
        user = UserRepository(db.session).get_by_id(user_id)
        if user is None:
            abort(404)
        if not user.is_active:
            abort(403, description="Account is deactivated.")
        return {"email": user.email}
    @blp.response(204)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def delete(self):
        try:
            user_id = uuid.UUID(str(get_jwt_identity()))
        except ValueError:
            abort(400, description="Invalid subject in token.")
        repo = UserRepository(db.session)
        if repo.deactivate(user_id) is None:
            abort(404)
        db.session.commit()


@blp.route("/me/password")
class ChangePassword(MethodView):
    @blp.arguments(PasswordChangeSchema)
    @blp.response(204)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def patch(self, payload):
        try:
            user_id = uuid.UUID(str(get_jwt_identity()))
        except ValueError:
            abort(400, description="Invalid subject in token.")
        repo = UserRepository(db.session)
        user = repo.get_by_id(user_id)
        if user is None:
            abort(404)
        if not user.is_active:
            abort(403, description="Account is deactivated.")
        if not SecurityService.check_password(
            payload["current_password"],
            user.hashed_password,
        ):
            abort(401, description="Current password is incorrect.")
        repo.update(
            user,
            hashed_password=SecurityService.hash_password(payload["new_password"]),
            access_jwt=None,
            refresh_jwt=None,
        )
        db.session.commit()
