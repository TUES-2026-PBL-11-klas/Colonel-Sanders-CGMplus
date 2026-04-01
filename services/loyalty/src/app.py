from flask import Flask
from src.extensions import (
    api,
    jwt
)
from src.routes.points import blp as PointBlueprint


def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.Config")

    api.init_app(app)
    jwt.init_app(app)


    api.register_blueprint(PointBlueprint)

    return app
