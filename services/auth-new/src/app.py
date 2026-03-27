from flask import Flask
from .extensions import api, db
from .routes.auth import blp as AuthBlueprint
from .routes.root import blp as RootBlueprint


def create_app():
    app = Flask(__name__)

    app.config.update({
        "API_TITLE": "User API",
        "API_VERSION": "v1",
        "OPENAPI_VERSION": "3.0.3",
        "OPENAPI_JSON_PATH": "openapi.json",
        "OPENAPI_URL_PREFIX": "/docs",
        "OPENAPI_SWAGGER_UI_PATH": "/",
        "OPENAPI_SWAGGER_UI_URL":
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    })

    api.init_app(app)
    # db.init_app(app)

    api.register_blueprint(AuthBlueprint, url_prefix="/auth")
    api.register_blueprint(RootBlueprint)

    return app


if __name__ == "__main__":
    app = create_app()
