from flask import Flask
from src.extensions import (
    api
)


def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.Config")

    api.init_app(app)

    return app
