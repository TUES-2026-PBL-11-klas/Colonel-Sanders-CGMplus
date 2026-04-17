from src.extensions import db


class BaseModel(db.Model):
    __abstract__ = True
