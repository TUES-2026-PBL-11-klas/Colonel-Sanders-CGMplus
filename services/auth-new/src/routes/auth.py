from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify

from src.schemas.token_schema import TokenResponseSchema
from src.schemas.login_schema import LoginSchema
from src.schemas.register_schema import RegisterSchema

blp = Blueprint("auth", "auth", url_prefix="/auth")


@blp.route("/register")
class Register(MethodView):
    @blp.arguments(RegisterSchema)
    @blp.response(201, TokenResponseSchema)
    def post(self):
        return jsonify({})


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    @blp.response(201, TokenResponseSchema)
    def post(self):
        return jsonify({})
