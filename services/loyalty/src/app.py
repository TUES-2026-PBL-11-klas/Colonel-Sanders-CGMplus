from flask import Flask
from src.extensions import (
    api,
    jwt,
    db,
    migrate
)
from src.models.profile import Profile  # noqa: F401
from src.models.card import Card  # noqa: F401
from src.models.offerModel import OfferModel # noqa: F401
from src.models.pointTransaction import PointTransaction # noqa: F401
from src.routes.profile import blp as PointBlueprint
from src.routes.internal import blp as InternalBlueprint
from src.routes.offers import blp as OfferBlueprint


def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.Config")

    db.init_app(app)
    api.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    api.register_blueprint(PointBlueprint, url_prefix="/api/v1/profile")
    api.register_blueprint(OfferBlueprint, url_prefix="/api/v1/offers")
    api.register_blueprint(InternalBlueprint)


    return app
