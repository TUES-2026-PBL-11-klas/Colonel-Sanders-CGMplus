from flask_smorest import Blueprint
from flask.views import MethodView
from src.schemas.health import HealthResponseSchema

blp = Blueprint("health", "health", url_prefix="/health")


@blp.route("/")
class Health(MethodView):
    @blp.response(200, HealthResponseSchema)
    def get(self):
        return {"status": "ok"}
