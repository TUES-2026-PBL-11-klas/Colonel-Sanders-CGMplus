from marshmallow import Schema, fields
from marshmallow.validate import Length, Regexp


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=[
            Length(min=8, error="Password must be at least 8 characters"),
            Regexp(r'(?=.*[A-Z])', error="Must contain an uppercase letter"),
            Regexp(r'(?=.*[0-9])', error="Must contain a digit"),
            Regexp(r'(?=.*[!@#$%^&*])', error="Must contain a special character"),
        ]
    )


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
