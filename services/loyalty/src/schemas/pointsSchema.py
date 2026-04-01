from marshmallow import Schema, fields


class PointInfoSchema(Schema):
    points = fields.Int(required=True)
