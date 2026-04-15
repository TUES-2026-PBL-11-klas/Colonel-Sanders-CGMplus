from flask_smorest import Blueprint
from flask.views import MethodView
from src.schemas.profileSchema import ProfileSchema, CardSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from src.models.card import Card as CardModel
from uuid import UUID

blp = Blueprint("profile", "profile", url_prefix="/profile")


@blp.route("/")
class Profile(MethodView):
    @blp.response(200, ProfileSchema)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        data = {
            "points": 67,
            "rank": "gold"
        }
        print(identity)
        return data


@blp.route("/card")
class Card(MethodView):
    @blp.response(200, CardSchema)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def get(self):
        profile_id = get_jwt_identity()
        card = CardModel.query.filter_by(id=UUID(profile_id)).first()

        if not card:
            return jsonify({'error': 'Card not found'}), 404

        return jsonify({'nfc_id': card.nfc_id})
