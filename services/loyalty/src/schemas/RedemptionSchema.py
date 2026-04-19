from marshmallow import Schema, fields


class RedemptionSchema(Schema):
    id = fields.UUID(dump_only=True)
    offer_id = fields.Int(required=True)
    profile_id = fields.UUID(required=True)
    points_cost = fields.Int(required=True)
