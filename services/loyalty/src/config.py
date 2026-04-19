from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Config:
    API_TITLE = "Profile API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_JSON_PATH = "openapi.json"
    OPENAPI_URL_PREFIX = "/docs"
    OPENAPI_SWAGGER_UI_PATH = "/"
    OPENAPI_SWAGGER_UI_URL = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    JWT_SECRET_KEY = getenv("JWT_SECRET")

    SQLALCHEMY_DATABASE_URI = getenv("DB_URL")
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
