from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from src.schemas.offersSchema import OfferSchema
from src.repositories.offerRepository import OfferRepository
from src.extensions import db
from src.services.offerService import OfferService

blp = Blueprint("Offers", "offers", url_prefix="/offers")

@blp.route("/")
class RootRoute(MethodView):
    @blp.response(200, OfferSchema(many=True))
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def get(self):
        offers = OfferRepository(db.session).get_active()
        return offers


@blp.route("/<int:offer_id>/redemption")
class ReedemRoute(MethodView):
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def post(self, offer_id):
        offer = OfferRepository(db.session).get_by_id(offer_id)
        OfferService.redeem_offer(offer_id)

        return offer # return something else
