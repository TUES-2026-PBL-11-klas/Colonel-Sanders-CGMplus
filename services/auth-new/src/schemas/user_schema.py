from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.validate import Length, Regexp


class UserMeResponseSchema(Schema):
    email = fields.Email(required=True)


class PasswordChangeSchema(Schema):
    current_password: str = fields.Str(required=True)
    new_password: str = fields.Str(
        required=True,
        validate=[
            Length(min=8, error="Password must be at least 8 characters"),
            Regexp(r'(?=.*[A-Z])', error="Must contain an uppercase letter"),
            Regexp(r'(?=.*[0-9])', error="Must contain a digit"),
            Regexp(r'(?=.*[!@#$%^&*])', error="Must contain a special character"),
        ]
    )

    @validates_schema
    def validate_passwords_differ(self, data, **kwargs):
        if data.get("current_password") == data.get("new_password"):
            raise ValidationError(
                "New password must differ from the current password",
                "new_password"
            )
