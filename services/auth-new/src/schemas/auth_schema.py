from marshmallow import Schema, fields


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class TokenRefreshSchema(Schema):
    refresh_token: str = fields.Str(required=True)


class TokenResponseSchema(Schema):
    access_token: str = fields.Str(required=True)
    refresh_token: str = fields.Str(required=True)
    token_type: str = fields.Str(
        required=True,
        default="bearer",
        dump_only=True,
        metadata={"default": "bearer"}
    )
