from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify
from src.schemas.internalSchema import CreateProfileSchema
from src.services.profile import ProfileService
from src.services.card import CardService


blp = Blueprint("internal", "internal", url_prefix="/internal")

@blp.route("/<string:account_id>/points")
class Points(MethodView):
    def patch(self, account_id):
        resp = ProfileService.update_points(account_id)
        if resp is None:
            resp = False

        return jsonify({
            'status': resp
        })


@blp.route("/profile")
class CreateProfile(MethodView):
    @blp.arguments(CreateProfileSchema)
    def post(self, args):
        profile = ProfileService.create_profile(args['uuid'])
        card = CardService.create_card(args['uuid'])

        return jsonify({
            'id': str(profile.id),
            'balance': profile.balance,
            'rank': profile.rank
        }), 201
