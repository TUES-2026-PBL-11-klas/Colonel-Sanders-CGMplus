from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from src.schemas.offersSchema import OfferSchema
from flask import jsonify

blp = Blueprint("Offers", "offers", url_prefix="/offers")

@blp.route("/")
class RootRoute(MethodView):
    @blp.response(200, OfferSchema(many=True))
    @blp.doc(security=[{"BearerAuth": []}])
    # @jwt_required()
    def get(self):
        offer1 = {
            'id': 1,
            'name': "OFFFER_1",
            'description': "my sigma 1 month card",
            'price': "2511"
        }
        offer2 = {
            'id': 2,
            'name': "OFFFER_2",
            'description': "my sigma 2 month card",
            'price': "1125"
        }
        return [
            offer1,
            offer2
        ]


@blp.route("/<int:offer_id>/redemption")
class ReedemRoute(MethodView):
    @blp.doc(security=[{"BearerAuth": []}])
    # @jwt_required()
    def post(self, offer_id):
        return jsonify({"offer_id": offer_id})
