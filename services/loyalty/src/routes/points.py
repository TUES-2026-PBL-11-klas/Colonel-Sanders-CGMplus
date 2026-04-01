from flask_smorest import Blueprint
from flask.views import MethodView
from src.schemas.pointsSchema import PointInfoSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

blp = Blueprint("points", "points", url_prefix="/points")

@blp.route("/points")
class Points(MethodView):
    @blp.response(200, PointInfoSchema)
    @blp.doc(security=[{"BearerAuth": []}])
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        points = {
            "points": 67,
        }
        return points
