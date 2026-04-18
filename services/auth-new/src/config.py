import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def get_config_name() -> str:
    env = (os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development").lower()
    if env in ("test", "testing"):
        return "testing"
    if env == "production":
        return "production"
    return "development"

def apply_runtime_config(app: Flask, name: str) -> None:
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
    app.config["DEBUG_METRICS"] = os.getenv("DEBUG_METRICS", "0") == "1"
    app.config["LOYALTY_SERVICE_URL"] = os.getenv("LOYALTY_SERVICE_URL", "http://loyalty-service:8000")
    if name == "development":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        )
    elif name == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:"
        )
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    elif name == "production":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        )


class Config:
    API_TITLE = "User API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_JSON_PATH = "openapi.json"
    OPENAPI_URL_PREFIX = "/docs"
    OPENAPI_SWAGGER_UI_PATH = "/"
    OPENAPI_SWAGGER_UI_URL = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    # JWT_SECRET_KEY = os.getenv("JWT_SECRET")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_SPEC_OPTIONS = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    }


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
