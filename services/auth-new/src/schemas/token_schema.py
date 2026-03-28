from marshmallow import Schema, fields


class TokenResponseSchema(Schema):
    access_token: str = fields.Str(required=True)
    refresh_token: str = fields.Str(required=True)
    token_type: str = fields.Str(
        required=True,
        default="bearer",
        dump_only=True,
        metadata={"default": "bearer"}
    )
