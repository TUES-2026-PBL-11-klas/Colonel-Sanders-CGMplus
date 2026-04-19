from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.schemas.profileSchema import ProfileSchema, CardSchema
from src.models.card import Card as CardModel
from src.repositories.ProfileRepositority import ProfileRepository
from src.extensions import db
from uuid import UUID

blp = Blueprint("profile", "profile", url_prefix="/profile")


@blp.route("/me")
class Profile(MethodView):
    @blp.response(200, ProfileSchema)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def get(self):
        profile_id_str = get_jwt_identity()
        try:
            profile_id = UUID(profile_id_str)
            profile = ProfileRepository(db.session).get_by_uuid(profile_id)
            if not profile:
                return jsonify({'error': 'Profile not found'}), 404

            return {
                'balance': profile.balance,
                'rank': profile.rank
            }
        except Exception:
            return jsonify({'error': 'Internal server error'}), 500


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

        return jsonify({
            'nfc_id': card.nfc_id,
            'active': card.active,
            'disabled': card.disabled,
            'expiry_date': card.expiry_date.isoformat()
        })
