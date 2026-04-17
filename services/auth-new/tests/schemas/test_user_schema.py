import pytest
from marshmallow import ValidationError

from src.schemas.user_schema import UserMeResponseSchema, PasswordChangeSchema


# ---------------------------------------------------------------------------
# UserMeResponseSchema
# ---------------------------------------------------------------------------

class TestUserMeResponseSchema:
    schema = UserMeResponseSchema()

    def test_valid_email_deserializes(self):
        result = self.schema.load({"email": "user@example.com"})
        assert result["email"] == "user@example.com"

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({})
        assert "email" in exc.value.messages

    def test_invalid_email_format_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"email": "not-an-email"})
        assert "email" in exc.value.messages

    def test_empty_email_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"email": ""})
        assert "email" in exc.value.messages

    def test_serialization_dumps(self):
        result = self.schema.dump({"email": "user@example.com"})
        assert result["email"] == "user@example.com"


# ---------------------------------------------------------------------------
# PasswordChangeSchema
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    "current_password": "OldPass1!",
    "new_password": "NewPass1!",
}


class TestPasswordChangeSchemaValidPayload:
    schema = PasswordChangeSchema()

    def test_valid_payload_deserializes(self):
        result = self.schema.load(VALID_PAYLOAD)
        assert result["current_password"] == "OldPass1!"
        assert result["new_password"] == "NewPass1!"

    def test_all_constraints_met_no_error(self):
        # Should not raise for a fully compliant payload.
        self.schema.load({"current_password": "anything", "new_password": "V4l!dPwd"})


class TestPasswordChangeSchemaRequiredFields:
    schema = PasswordChangeSchema()

    def test_missing_current_password_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"new_password": "NewPass1!"})
        assert "current_password" in exc.value.messages

    def test_missing_new_password_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "OldPass1!"})
        assert "new_password" in exc.value.messages

    def test_empty_payload_raises_both_fields(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({})
        assert "current_password" in exc.value.messages
        assert "new_password" in exc.value.messages


class TestPasswordChangeSchemaNewPasswordLength:
    schema = PasswordChangeSchema()

    def test_new_password_too_short_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "OldPass1!", "new_password": "Sh0rt!"})
        errors = exc.value.messages.get("new_password", [])
        assert any("8 characters" in e for e in errors)

    def test_new_password_exactly_8_chars_is_accepted(self):
        self.schema.load({"current_password": "OldPass1!", "new_password": "Abcde1!x"})

    def test_new_password_longer_than_8_chars_is_accepted(self):
        self.schema.load({"current_password": "OldPass1!", "new_password": "LongPassword1!"})


class TestPasswordChangeSchemaNewPasswordComplexity:
    schema = PasswordChangeSchema()

    def test_missing_uppercase_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "OldPass1!", "new_password": "nouppercase1!"})
        errors = exc.value.messages.get("new_password", [])
        assert any("uppercase" in e for e in errors)

    def test_missing_digit_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "OldPass1!", "new_password": "NoDigitHere!"})
        errors = exc.value.messages.get("new_password", [])
        assert any("digit" in e for e in errors)

    def test_missing_special_character_raises(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "OldPass1!", "new_password": "NoSpecial1A"})
        errors = exc.value.messages.get("new_password", [])
        assert any("special character" in e for e in errors)

    def test_multiple_violations_reported_together(self):
        # No uppercase, no digit, no special char, too short.
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "OldPass1!", "new_password": "bad"})
        errors = exc.value.messages.get("new_password", [])
        assert len(errors) >= 2

    @pytest.mark.parametrize("special_char", list("!@#$%^&*"))
    def test_each_allowed_special_character_is_accepted(self, special_char):
        pw = f"ValidPass1{special_char}"
        self.schema.load({"current_password": "OldPass1!", "new_password": pw})


class TestPasswordChangeSchemaPasswordsDiffer:
    schema = PasswordChangeSchema()

    def test_same_passwords_raise_validation_error(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "SamePass1!", "new_password": "SamePass1!"})
        assert "new_password" in exc.value.messages
        assert any(
            "differ" in e for e in exc.value.messages["new_password"]
        )

    def test_different_passwords_do_not_raise(self):
        self.schema.load({"current_password": "OldPass1!", "new_password": "NewPass1!"})

    def test_same_password_error_is_on_new_password_field(self):
        with pytest.raises(ValidationError) as exc:
            self.schema.load({"current_password": "SamePass1!", "new_password": "SamePass1!"})
        # Error must be attached to new_password, not _schema.
        assert "new_password" in exc.value.messages
        assert "_schema" not in exc.value.messages
