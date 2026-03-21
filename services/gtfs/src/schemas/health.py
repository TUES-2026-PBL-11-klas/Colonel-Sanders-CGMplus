from marshmallow import Schema, fields

class HealthResponseSchema(Schema):
    status = fields.String(required=True)
