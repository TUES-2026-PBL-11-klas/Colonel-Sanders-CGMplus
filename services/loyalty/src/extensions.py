from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

api = Api()
jwt = JWTManager()
db = SQLAlchemy()
