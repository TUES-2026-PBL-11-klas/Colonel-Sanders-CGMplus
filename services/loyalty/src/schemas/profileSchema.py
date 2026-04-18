from marshmallow import Schema, fields


class ProfileSchema(Schema):
    balance = fields.Int(required=True)
    rank = fields.String(required=True)


class CardSchema(Schema):
    nfc_id = fields.String()
    active = fields.Boolean()
    disabled = fields.Boolean()
    expiry_date = fields.DateTime()
