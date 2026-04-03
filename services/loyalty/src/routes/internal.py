from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify


blp = Blueprint("internal", "internal", url_prefix="/internal")

@blp.route("/<string:account_id>/points")
class Points(MethodView):
    def patch(self, account_id):
        account_id = account_id
        return jsonify({})
