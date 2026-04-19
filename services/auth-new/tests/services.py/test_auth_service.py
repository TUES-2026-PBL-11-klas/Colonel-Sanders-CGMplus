import uuid
import secrets
from unittest.mock import MagicMock, patch, call
import pytest
import jwt as pyjwt

from src.exceptions.auth_exceptions import ResourceConflictError, InvalidCredentialsError
from src.services.auth_service import AuthService


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

JWT_SECRET = "test-secret"
USER_ID = uuid.uuid4()
USER_EMAIL = "user@example.com"
USER_PASSWORD = "plaintext-password"
HASHED_PASSWORD = "$2b$12$hashedvalue"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def user_repo():
    return MagicMock()


@pytest.fixture()
def role_repo():
    return MagicMock()


@pytest.fixture()
def service(user_repo, role_repo):
    return AuthService(user_repo=user_repo, role_repo=role_repo)


@pytest.fixture()
def mock_user():
    user = MagicMock()
    user.id = USER_ID
    user.email = USER_EMAIL
    user.hashed_password = HASHED_PASSWORD
    user.is_active = True
    user.refresh_jwt = None
    return user


@pytest.fixture()
def mock_role():
    role = MagicMock()
    role.id = uuid.uuid4()
    return role


# Patch flask_jwt_extended token creators globally for every test in this module.
@pytest.fixture(autouse=True)
def patch_token_creators():
    with patch("src.services.auth_service.create_access_token", return_value="access-tok") as mock_access, \
         patch("src.services.auth_service.create_refresh_token", return_value="refresh-tok") as mock_refresh:
        yield mock_access, mock_refresh


# ---------------------------------------------------------------------------
# AuthService.register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_raises_conflict_when_email_already_exists(self, service, user_repo, mock_user):
        user_repo.get_by_email.return_value = mock_user

        with pytest.raises(ResourceConflictError, match="already exists"):
            service.register(USER_EMAIL, USER_PASSWORD)

    def test_creates_user_with_existing_role(self, service, user_repo, role_repo, mock_user, mock_role):
        user_repo.get_by_email.return_value = None
        role_repo.get_by_name.return_value = mock_role
        user_repo.create.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.hash_password", return_value=HASHED_PASSWORD):
            result = service.register(USER_EMAIL, USER_PASSWORD)

        role_repo.get_by_name.assert_called_once_with("user")
        role_repo.create.assert_not_called()
        user_repo.create.assert_called_once_with(
            email=USER_EMAIL,
            hashed_password=HASHED_PASSWORD,
            role_id=mock_role.id,
        )
        assert result["token_type"] == "bearer"

    def test_creates_role_when_not_found(self, service, user_repo, role_repo, mock_user, mock_role):
        user_repo.get_by_email.return_value = None
        role_repo.get_by_name.return_value = None
        role_repo.create.return_value = mock_role
        user_repo.create.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.hash_password", return_value=HASHED_PASSWORD):
            service.register(USER_EMAIL, USER_PASSWORD)

        role_repo.create.assert_called_once_with(role="user")
        # Flush is called after creating role and after creating user
        assert user_repo.session.flush.call_count >= 1

    def test_hashes_password_before_storing(self, service, user_repo, role_repo, mock_user, mock_role):
        user_repo.get_by_email.return_value = None
        role_repo.get_by_name.return_value = mock_role
        user_repo.create.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.hash_password", return_value=HASHED_PASSWORD) as mock_hash:
            service.register(USER_EMAIL, USER_PASSWORD)

        mock_hash.assert_called_once_with(USER_PASSWORD)

    def test_returns_token_dict(self, service, user_repo, role_repo, mock_user, mock_role):
        user_repo.get_by_email.return_value = None
        role_repo.get_by_name.return_value = mock_role
        user_repo.create.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.hash_password", return_value=HASHED_PASSWORD):
            result = service.register(USER_EMAIL, USER_PASSWORD)

        assert result == {"access_token": "access-tok", "refresh_token": "refresh-tok", "token_type": "bearer"}

    def test_persists_tokens_on_user(self, service, user_repo, role_repo, mock_user, mock_role):
        user_repo.get_by_email.return_value = None
        role_repo.get_by_name.return_value = mock_role
        user_repo.create.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.hash_password", return_value=HASHED_PASSWORD):
            service.register(USER_EMAIL, USER_PASSWORD)

        user_repo.update.assert_called_once_with(
            mock_user,
            access_jwt="access-tok",
            refresh_jwt="refresh-tok",
        )


# ---------------------------------------------------------------------------
# AuthService.login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_raises_when_user_not_found(self, service, user_repo):
        user_repo.get_by_email.return_value = None

        with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
            service.login(USER_EMAIL, USER_PASSWORD)

    def test_raises_when_user_inactive(self, service, user_repo, mock_user):
        mock_user.is_active = False
        user_repo.get_by_email.return_value = mock_user

        with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
            service.login(USER_EMAIL, USER_PASSWORD)

    def test_raises_when_password_wrong(self, service, user_repo, mock_user):
        user_repo.get_by_email.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.check_password", return_value=False):
            with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
                service.login(USER_EMAIL, "wrong-password")

    def test_returns_tokens_on_success(self, service, user_repo, mock_user):
        user_repo.get_by_email.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.check_password", return_value=True):
            result = service.login(USER_EMAIL, USER_PASSWORD)

        assert result == {"access_token": "access-tok", "refresh_token": "refresh-tok", "token_type": "bearer"}

    def test_persists_tokens_after_login(self, service, user_repo, mock_user):
        user_repo.get_by_email.return_value = mock_user

        with patch("src.services.auth_service.SecurityService.check_password", return_value=True):
            service.login(USER_EMAIL, USER_PASSWORD)

        user_repo.update.assert_called_once_with(
            mock_user,
            access_jwt="access-tok",
            refresh_jwt="refresh-tok",
        )


# ---------------------------------------------------------------------------
# AuthService.refresh
# ---------------------------------------------------------------------------

def _make_refresh_token(user_id: uuid.UUID, secret: str = JWT_SECRET) -> str:
    """Helper: creates a minimal HS256 token that mirrors the real payload shape."""
    return pyjwt.encode({"sub": str(user_id)}, secret, algorithm="HS256")


class TestRefresh:
    def test_raises_on_invalid_jwt_signature(self, service):
        bad_token = _make_refresh_token(USER_ID, secret="wrong-secret")

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(bad_token, JWT_SECRET)

    def test_raises_on_expired_token(self, service):
        import time
        expired = pyjwt.encode(
            {"sub": str(USER_ID), "exp": int(time.time()) - 10},
            JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(expired, JWT_SECRET)

    def test_raises_when_sub_missing_from_payload(self, service):
        token_no_sub = pyjwt.encode({}, JWT_SECRET, algorithm="HS256")

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(token_no_sub, JWT_SECRET)

    def test_raises_when_sub_not_valid_uuid(self, service):
        token_bad_sub = pyjwt.encode({"sub": "not-a-uuid"}, JWT_SECRET, algorithm="HS256")

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(token_bad_sub, JWT_SECRET)

    def test_raises_when_user_not_found(self, service, user_repo):
        token = _make_refresh_token(USER_ID)
        user_repo.get_by_id.return_value = None

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(token, JWT_SECRET)

    def test_raises_when_user_inactive(self, service, user_repo, mock_user):
        token = _make_refresh_token(USER_ID)
        mock_user.is_active = False
        user_repo.get_by_id.return_value = mock_user

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(token, JWT_SECRET)

    def test_raises_when_stored_refresh_jwt_is_none(self, service, user_repo, mock_user):
        token = _make_refresh_token(USER_ID)
        mock_user.refresh_jwt = None
        user_repo.get_by_id.return_value = mock_user

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(token, JWT_SECRET)

    def test_raises_on_token_length_mismatch(self, service, user_repo, mock_user):
        token = _make_refresh_token(USER_ID)
        mock_user.refresh_jwt = token + "extra"
        user_repo.get_by_id.return_value = mock_user

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(token, JWT_SECRET)

    def test_raises_on_token_digest_mismatch(self, service, user_repo, mock_user):
        token = _make_refresh_token(USER_ID)
        # Same length, different content — triggers compare_digest failure.
        mock_user.refresh_jwt = "x" * len(token)
        user_repo.get_by_id.return_value = mock_user

        with pytest.raises(InvalidCredentialsError, match="Invalid or expired"):
            service.refresh(token, JWT_SECRET)

    def test_returns_new_tokens_on_valid_refresh(self, service, user_repo, mock_user):
        token = _make_refresh_token(USER_ID)
        mock_user.refresh_jwt = token
        user_repo.get_by_id.return_value = mock_user

        result = service.refresh(token, JWT_SECRET)

        assert result == {"access_token": "access-tok", "refresh_token": "refresh-tok", "token_type": "bearer"}

    def test_persists_new_tokens_after_refresh(self, service, user_repo, mock_user):
        token = _make_refresh_token(USER_ID)
        mock_user.refresh_jwt = token
        user_repo.get_by_id.return_value = mock_user

        service.refresh(token, JWT_SECRET)

        user_repo.update.assert_called_once_with(
            mock_user,
            access_jwt="access-tok",
            refresh_jwt="refresh-tok",
        )

    def test_looks_up_user_by_correct_uuid(self, service, user_repo, mock_user):
        token = _make_refresh_token(USER_ID)
        mock_user.refresh_jwt = token
        user_repo.get_by_id.return_value = mock_user

        service.refresh(token, JWT_SECRET)

        user_repo.get_by_id.assert_called_once_with(USER_ID)


# ---------------------------------------------------------------------------
# AuthService._issue_tokens (indirectly via register/login, but also directly)
# ---------------------------------------------------------------------------

class TestIssueTokens:
    def test_creates_access_and_refresh_tokens_with_user_id_as_identity(
        self, service, patch_token_creators, mock_user
    ):
        mock_access, mock_refresh = patch_token_creators
        service._issue_tokens(mock_user)

        mock_access.assert_called_once_with(identity=str(USER_ID))
        mock_refresh.assert_called_once_with(identity=str(USER_ID))

    def test_token_type_is_bearer(self, service, mock_user):
        result = service._issue_tokens(mock_user)
        assert result["token_type"] == "bearer"

    def test_both_tokens_present_in_result(self, service, mock_user):
        result = service._issue_tokens(mock_user)
        assert "access_token" in result
        assert "refresh_token" in result
