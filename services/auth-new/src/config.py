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


def build_db_uri_from_parts() -> str | None:
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB")

    if all([user, password, host, database]):
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return None

def apply_runtime_config(app: Flask, name: str) -> None:
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
    app.config["DEBUG_METRICS"] = os.getenv("DEBUG_METRICS", "0") == "1"
    sqlalchemy_uri = os.getenv("SQLALCHEMY_DATABASE_URI") or build_db_uri_from_parts()
    if name == "development":
        app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        )
    elif name == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:"
        )
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    elif name == "production":
        app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        )
    app.config["LOYALTY_SERVICE_URL"] = os.getenv("LOYALTY_SERVICE_URL", "http://loyalty:5000")


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
