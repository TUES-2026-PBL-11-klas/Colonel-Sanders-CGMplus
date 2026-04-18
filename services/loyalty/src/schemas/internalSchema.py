from marshmallow import Schema, fields


class CreateProfileSchema(Schema):
    uuid = fields.UUID(required=True)
