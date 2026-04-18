from marshmallow import Schema, fields


class OfferSchema(Schema):
    id = fields.Int(required=True)
    name = fields.String(required=True)
    description = fields.String()
    price = fields.Int(required=True)
