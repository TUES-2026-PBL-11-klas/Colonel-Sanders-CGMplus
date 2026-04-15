from marshmallow import Schema, fields


class ProfileSchema(Schema):
    points = fields.Int(required=True)
    rank = fields.String(required=True)


class CardSchema(Schema):
    card = fields.Str(len=16)
