import os
from flask import Flask
from flask_migrate import Migrate
from src.extensions import api, db
from src.routes.auth import blp as AuthBlueprint
from src.routes.root import blp as RootBlueprint
from dotenv import load_dotenv

load_dotenv()


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
        "SQLALCHEMY_DATABASE_URI": os.getenv("SQLALCHEMY_DATABASE_URI")
    })

    api.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    migrate.init_app(app, db)

    from src import models

    api.register_blueprint(AuthBlueprint, url_prefix="/auth")
    api.register_blueprint(RootBlueprint)

    return app


if __name__ == "__main__":
    app = create_app()
