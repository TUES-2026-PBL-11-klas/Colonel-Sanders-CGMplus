from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

api = Api()
jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
