from flask import Flask
from src.extensions import api
from src.routes.health import blp as HealthBlueprint

def create_app():
    app = Flask(__name__)

    app.config.update({
        "API_TITLE": "My Microservice",
        "API_VERSION": "v1",
        "OPENAPI_VERSION": "3.0.3",
        "OPENAPI_JSON_PATH": "openapi.json",
        "OPENAPI_URL_PREFIX": "/docs",
        "OPENAPI_SWAGGER_UI_PATH": "/",
        "OPENAPI_SWAGGER_UI_URL": "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    })

    api.init_app(app)
    api.register_blueprint(HealthBlueprint)

    return app
