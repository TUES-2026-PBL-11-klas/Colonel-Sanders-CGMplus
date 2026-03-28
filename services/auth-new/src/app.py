import os
from flask import Flask
from flask_migrate import Migrate
from src.extensions import api, db, migrate, jwt
from src.routes.auth import blp as AuthBlueprint
from src.routes.root import blp as RootBlueprint
from src.routes.user import blp as UserBlueprint
from dotenv import load_dotenv

load_dotenv()


def _jwt_secret_key() -> str:
    key = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
    if key:
        return key
    return "dev-only-insecure-jwt-key-set-JWT_SECRET-or-SECRET_KEY"


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
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
        "SQLALCHEMY_TRACK_MODIFICATIONS": os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS"),
        "SQLALCHEMY_DATABASE_URI": os.getenv("SQLALCHEMY_DATABASE_URI"),
        "JWT_SECRET_KEY": _jwt_secret_key(),
    })
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    #"security": [{"BearerAuth": []}],  # applies globally to all endpoints
    }

    api.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from src import models

    api.register_blueprint(AuthBlueprint, url_prefix="/auth")
    api.register_blueprint(RootBlueprint)
    api.register_blueprint(UserBlueprint)

    return app


if __name__ == "__main__":
    app = create_app()
