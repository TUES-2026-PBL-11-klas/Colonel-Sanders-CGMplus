from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify
from flask import redirect

blp = Blueprint("root", "root")


@blp.route("/")
class Root(MethodView):
    def get(self):
        return redirect("/docs")


@blp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
