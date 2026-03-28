from marshmallow import Schema, fields


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
