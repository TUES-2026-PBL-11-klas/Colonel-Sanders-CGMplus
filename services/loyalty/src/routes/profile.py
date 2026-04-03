from flask_smorest import Blueprint
from flask.views import MethodView
from src.schemas.profileSchema import ProfileSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

blp = Blueprint("points", "points", url_prefix="/points")

@blp.route("/profile")
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
