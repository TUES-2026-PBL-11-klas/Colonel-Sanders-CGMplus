from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify, abort
from src.schemas.internalSchema import CreateProfileSchema
from src.services.ProfileService import ProfileService
from src.services.CardService import CardService
from src.services.PointService import PointService
from src.extensions import db
import uuid


blp = Blueprint("internal", "internal", url_prefix="/internal")


@blp.route("/<string:account_id>/points")
class Points(MethodView):
    def patch(self, account_id):
        try:
            uuid.UUID(account_id, version=4)
        except ValueError:
            abort(400, description="Invalid account_id: must be a valid UUID.")

        resp = PointService.add_points(account_id)
        return jsonify({
            'status': resp
        })


@blp.route("/profile")
class CreateProfile(MethodView):
    @blp.arguments(CreateProfileSchema)
    def post(self, args):
        try:
            profile = ProfileService.create_profile(args['uuid'])
            card = CardService.create_card(args['uuid'])

            if not profile or not card:
                db.session.rollback()
                return jsonify({'error': 'Failed to create profile'}), 500

            return jsonify({
                'id': str(profile.id),
                'balance': profile.balance,
                'rank': profile.rank
            }), 201
        except Exception:
            db.session.rollback()
            return jsonify({'error': 'Profile creation failed'}), 500
