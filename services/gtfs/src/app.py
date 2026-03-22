from flask import Flask
from .util.scheduler import start_scheduler
from src.extensions import api
from src.routes.health import blp as HealthBlueprint
from src.routes.root import blp as RootBlueprint
from src.routes.realtime import blp as RealtimeBlueprint
from src.routes.static import blp as StaticBlueprint


def create_app():
    app = Flask(__name__)

    app.config.update({
        "API_TITLE": "GTFS Microservice",
        "API_VERSION": "v1",
        "OPENAPI_VERSION": "3.0.3",
        "OPENAPI_JSON_PATH": "openapi.json",
        "OPENAPI_URL_PREFIX": "/docs",
        "OPENAPI_SWAGGER_UI_PATH": "/",
        "OPENAPI_SWAGGER_UI_URL":
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    })

    api.init_app(app)
    api.register_blueprint(HealthBlueprint)
    api.register_blueprint(RootBlueprint)
    api.register_blueprint(RealtimeBlueprint, url_prefix="/api/v1/realtime")
    api.register_blueprint(StaticBlueprint, url_prefix="/api/v1/static")

    start_scheduler()

    return app
