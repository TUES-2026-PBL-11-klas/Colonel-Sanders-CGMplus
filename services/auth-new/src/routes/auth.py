from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify

blp = Blueprint("auth", "auth", url_prefix="/auth")


@blp.route("/register")
class Register(MethodView):
    def post(self):
        return jsonify({})


@blp.route("/login")
class Login(MethodView):
    def post(self):
        return jsonify({})
