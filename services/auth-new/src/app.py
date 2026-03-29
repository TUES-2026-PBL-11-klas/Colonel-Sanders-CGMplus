from flask import Flask
from flask_migrate import Migrate

from src.config import apply_runtime_config, config_by_name, get_config_name
from src.extensions import api, db, migrate, jwt
from src.routes.auth import blp as AuthBlueprint
from src.routes.root import blp as RootBlueprint
from src.routes.user import blp as UserBlueprint

# load_dotenv()


def create_app(config_name: str | None = None):
    app = Flask(__name__)

    name = config_name or get_config_name()
    app.config.from_object(config_by_name[name])
    apply_runtime_config(app, name)

    if name == "production" and not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError(
            "JWT_SECRET_KEY is required in production. Set JWT_SECRET or SECRET_KEY."
        )

    api.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from src import models  # noqa: F401

    api.register_blueprint(AuthBlueprint, url_prefix="/auth")
    api.register_blueprint(RootBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
