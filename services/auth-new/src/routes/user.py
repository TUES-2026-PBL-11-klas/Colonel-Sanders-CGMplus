from flask_smorest import Blueprint
from flask.views import MethodView
from src.schemas.user_schema import PasswordChangeSchema
from flask_jwt_extended import jwt_required

blp = Blueprint("users", "users", url_prefix="/users")


@blp.route("/me")
class UserView(MethodView):
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def get(self):
        pass
    @blp.response(204)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def delete(self):
        pass


@blp.route("/me/password")
class Login(MethodView):
    @blp.arguments(PasswordChangeSchema)
    @blp.response(204)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def patch(self, payload):
        pass
