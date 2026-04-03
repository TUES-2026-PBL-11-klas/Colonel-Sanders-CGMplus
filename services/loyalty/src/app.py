from flask import Flask
from src.extensions import (
    api,
    jwt
)
from src.routes.profile import blp as PointBlueprint
from src.routes.internal import blp as InternalBlueprint


def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.Config")

    api.init_app(app)
    jwt.init_app(app)


    api.register_blueprint(PointBlueprint)
    api.register_blueprint(InternalBlueprint)

    return app
