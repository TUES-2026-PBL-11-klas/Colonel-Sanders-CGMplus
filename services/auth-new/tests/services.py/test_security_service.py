import bcrypt
import pytest

from src.services.security_service import SecurityService


class TestHashPassword:
    def test_returns_string(self):
        result = SecurityService.hash_password("password123")
        assert isinstance(result, str)

    def test_output_is_valid_bcrypt_hash(self):
        result = SecurityService.hash_password("password123")
        assert result.startswith("$2b$")

    def test_uses_12_rounds(self):
        result = SecurityService.hash_password("password123")
        # bcrypt hash format: $2b$<rounds>$...
        rounds = int(result.split("$")[2])
        assert rounds == 12

    def test_hash_differs_from_plaintext(self):
        password = "my-secret"
        assert SecurityService.hash_password(password) != password

    def test_two_hashes_of_same_password_are_different(self):
        """bcrypt salts must be random — identical inputs must not produce identical hashes."""
        h1 = SecurityService.hash_password("same-password")
        h2 = SecurityService.hash_password("same-password")
        assert h1 != h2

    def test_different_passwords_produce_different_hashes(self):
        assert SecurityService.hash_password("abc") != SecurityService.hash_password("xyz")

    def test_handles_empty_string(self):
        result = SecurityService.hash_password("")
        assert isinstance(result, str)
        assert result.startswith("$2b$")

    def test_handles_unicode_password(self):
        result = SecurityService.hash_password("pässwörد🔐")
        assert isinstance(result, str)
        assert result.startswith("$2b$")

    def test_rejects_password_longer_than_72_bytes(self):
        long_pw = "a" * 100
        with pytest.raises(ValueError, match="72 bytes"):
            SecurityService.hash_password(long_pw)


class TestCheckPassword:
    def test_returns_true_for_correct_password(self):
        password = "correct-horse"
        hashed = SecurityService.hash_password(password)
        assert SecurityService.check_password(password, hashed) is True

    def test_returns_false_for_wrong_password(self):
        hashed = SecurityService.hash_password("correct-horse")
        assert SecurityService.check_password("wrong-horse", hashed) is False

    def test_returns_false_for_empty_password_against_real_hash(self):
        hashed = SecurityService.hash_password("notempty")
        assert SecurityService.check_password("", hashed) is False

    def test_returns_true_for_empty_string_hashed_and_checked(self):
        hashed = SecurityService.hash_password("")
        assert SecurityService.check_password("", hashed) is True

    def test_case_sensitive(self):
        hashed = SecurityService.hash_password("Password")
        assert SecurityService.check_password("password", hashed) is False

    def test_handles_unicode_round_trip(self):
        password = "pässwörد🔐"
        hashed = SecurityService.hash_password(password)
        assert SecurityService.check_password(password, hashed) is True

    def test_returns_bool_not_truthy(self):
        """Ensure the return type is exactly bool, not a bcrypt truthy value."""
        hashed = SecurityService.hash_password("pw")
        result = SecurityService.check_password("pw", hashed)
        assert type(result) is bool  # noqa: E721

    def test_hash_generated_externally_is_accepted(self):
        """check_password must work with any valid bcrypt string, not just ones
        produced by hash_password."""
        password = "external"
        external_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
        assert SecurityService.check_password(password, external_hash) is True


class TestHashThenCheck:
    """Round-trip integration tests."""

    @pytest.mark.parametrize("password", [
        "simple",
        "C0mpl3x!@#$%^&*()",
        "with spaces in it",
        "unicode-pässwörd",
        "a" * 71,   # just under bcrypt's 72-byte truncation limit
    ])
    def test_round_trip(self, password):
        hashed = SecurityService.hash_password(password)
        assert SecurityService.check_password(password, hashed) is True

    @pytest.mark.parametrize("password", [
        "simple",
        "C0mpl3x!@#$%^&*()",
    ])
    def test_wrong_password_always_fails(self, password):
        hashed = SecurityService.hash_password(password)
        assert SecurityService.check_password(password + "X", hashed) is False
