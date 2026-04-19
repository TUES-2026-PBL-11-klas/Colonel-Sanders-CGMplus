from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.schemas.offersSchema import OfferSchema
from src.schemas.RedemptionSchema import RedemptionSchema
from src.repositories.offerRepository import OfferRepository
from src.repositories.RedemptionRepository import RedemptionRepository
from src.extensions import db
from src.services.OfferService import OfferService
from src.exceptions.OfferExceptions import InsufficientFunds
from flask import jsonify
from uuid import UUID

blp = Blueprint("Offers", "offers", description="Loyalty offers and redemptions endpoints.")


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
        profile_id_str = get_jwt_identity()
        try:
            profile_id = UUID(profile_id_str)
            OfferService.redeem_offer(offer_id, profile_id)
        except InsufficientFunds:
            return jsonify({
                "error": "Insufficient funds"
            }), 402
        except Exception:
            return jsonify({
                "error": "Failed to redeem offer"
            }), 500

        return jsonify({
            "status": "completed"
        }), 201


@blp.route("/redemptions")
class RedemptionsRoute(MethodView):
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(200, RedemptionSchema(many=True))
    @jwt_required()
    def get(self):
        profile_id_str = get_jwt_identity()
        try:
            profile_id = UUID(profile_id_str)
            redemptions = RedemptionRepository(
                db.session
            ).get_by_profile_id(profile_id)
            return redemptions
        except Exception:
            return jsonify({
                "error": "Failed to get redemptions"
            }), 500
