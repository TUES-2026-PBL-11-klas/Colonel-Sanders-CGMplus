import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from src.exceptions.auth_exceptions import ResourceConflictError, InvalidCredentialsError


# ---------------------------------------------------------------------------
# App fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    flask_app = Flask(__name__)
    flask_app.config.update(
        TESTING=True,
        API_TITLE="Test",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
        JWT_SECRET_KEY="test-secret",
        PROPAGATE_EXCEPTIONS=True,
    )

    JWTManager(flask_app)
    api = Api(flask_app)

    from src.routes.auth import blp
    api.register_blueprint(blp, url_prefix="/auth")

    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOKEN_RESPONSE = {
    "access_token": "access-tok",
    "refresh_token": "refresh-tok",
    "token_type": "bearer",
}

VALID_REGISTER_PAYLOAD = {"email": "new@example.com", "password": "ValidPass1!"}
VALID_LOGIN_PAYLOAD    = {"email": "user@example.com", "password": "ValidPass1!"}
VALID_REFRESH_PAYLOAD  = {"refresh_token": "some-refresh-token"}


def _service_patch(method: str, return_value=None, side_effect=None):
    """Patch a single method on AuthService, as used inside the route module."""
    target = f"src.routes.auth.AuthService.{method}"
    return patch(target, return_value=return_value, side_effect=side_effect)


def _db_patch():
    return patch("src.routes.auth.db")


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    URL = "/auth/register"

    def test_returns_201_and_tokens_on_success(self, client):
        with _service_patch("register", return_value=TOKEN_RESPONSE), _db_patch():
            resp = client.post(self.URL, json=VALID_REGISTER_PAYLOAD)

        assert resp.status_code == 201
        assert resp.get_json()["access_token"] == "access-tok"
        assert resp.get_json()["refresh_token"] == "refresh-tok"

    def test_commits_session_on_success(self, client):
        with _service_patch("register", return_value=TOKEN_RESPONSE), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_REGISTER_PAYLOAD)

        mock_db.session.commit.assert_called_once()

    def test_returns_409_on_conflict(self, client):
        with _service_patch("register", side_effect=ResourceConflictError("exists")), \
             _db_patch():
            resp = client.post(self.URL, json=VALID_REGISTER_PAYLOAD)

        assert resp.status_code == 409

    def test_rolls_back_on_conflict(self, client):
        with _service_patch("register", side_effect=ResourceConflictError("exists")), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_REGISTER_PAYLOAD)

        mock_db.session.rollback.assert_called_once()

    def test_does_not_commit_on_conflict(self, client):
        with _service_patch("register", side_effect=ResourceConflictError("exists")), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_REGISTER_PAYLOAD)

        mock_db.session.commit.assert_not_called()

    def test_returns_422_on_missing_email(self, client):
        resp = client.post(self.URL, json={"password": "ValidPass1!"})
        assert resp.status_code == 422

    def test_returns_422_on_missing_password(self, client):
        resp = client.post(self.URL, json={"email": "user@example.com"})
        assert resp.status_code == 422

    def test_returns_422_on_invalid_email_format(self, client):
        resp = client.post(self.URL, json={"email": "not-an-email", "password": "ValidPass1!"})
        assert resp.status_code == 422

    def test_service_called_with_correct_args(self, client):
        with _service_patch("register", return_value=TOKEN_RESPONSE) as mock_register, \
             _db_patch():
            client.post(self.URL, json=VALID_REGISTER_PAYLOAD)

        mock_register.assert_called_once_with(
            email="new@example.com",
            password="ValidPass1!",
        )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    URL = "/auth/login"

    def test_returns_200_and_tokens_on_success(self, client):
        with _service_patch("login", return_value=TOKEN_RESPONSE), _db_patch():
            resp = client.post(self.URL, json=VALID_LOGIN_PAYLOAD)

        assert resp.status_code == 200
        assert resp.get_json()["access_token"] == "access-tok"

    def test_commits_session_on_success(self, client):
        with _service_patch("login", return_value=TOKEN_RESPONSE), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_LOGIN_PAYLOAD)

        mock_db.session.commit.assert_called_once()

    def test_returns_401_on_invalid_credentials(self, client):
        with _service_patch("login", side_effect=InvalidCredentialsError("bad creds")), \
             _db_patch():
            resp = client.post(self.URL, json=VALID_LOGIN_PAYLOAD)

        assert resp.status_code == 401

    def test_rolls_back_on_invalid_credentials(self, client):
        with _service_patch("login", side_effect=InvalidCredentialsError("bad creds")), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_LOGIN_PAYLOAD)

        mock_db.session.rollback.assert_called_once()

    def test_does_not_commit_on_invalid_credentials(self, client):
        with _service_patch("login", side_effect=InvalidCredentialsError("bad creds")), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_LOGIN_PAYLOAD)

        mock_db.session.commit.assert_not_called()

    def test_returns_422_on_missing_fields(self, client):
        resp = client.post(self.URL, json={})
        assert resp.status_code == 422

    def test_service_called_with_correct_args(self, client):
        with _service_patch("login", return_value=TOKEN_RESPONSE) as mock_login, \
             _db_patch():
            client.post(self.URL, json=VALID_LOGIN_PAYLOAD)

        mock_login.assert_called_once_with(
            email="user@example.com",
            password="ValidPass1!",
        )


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

class TestRefresh:
    URL = "/auth/refresh"

    def test_returns_200_and_tokens_on_success(self, client):
        with _service_patch("refresh", return_value=TOKEN_RESPONSE), _db_patch():
            resp = client.post(self.URL, json=VALID_REFRESH_PAYLOAD)

        assert resp.status_code == 200
        assert resp.get_json()["refresh_token"] == "refresh-tok"

    def test_commits_session_on_success(self, client):
        with _service_patch("refresh", return_value=TOKEN_RESPONSE), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_REFRESH_PAYLOAD)

        mock_db.session.commit.assert_called_once()

    def test_returns_401_on_invalid_token(self, client):
        with _service_patch("refresh", side_effect=InvalidCredentialsError("bad token")), \
             _db_patch():
            resp = client.post(self.URL, json=VALID_REFRESH_PAYLOAD)

        assert resp.status_code == 401

    def test_rolls_back_on_invalid_token(self, client):
        with _service_patch("refresh", side_effect=InvalidCredentialsError("bad token")), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_REFRESH_PAYLOAD)

        mock_db.session.rollback.assert_called_once()

    def test_does_not_commit_on_invalid_token(self, client):
        with _service_patch("refresh", side_effect=InvalidCredentialsError("bad token")), \
             _db_patch() as mock_db:
            client.post(self.URL, json=VALID_REFRESH_PAYLOAD)

        mock_db.session.commit.assert_not_called()

    def test_returns_422_on_missing_refresh_token(self, client):
        resp = client.post(self.URL, json={})
        assert resp.status_code == 422

    def test_service_called_with_token_and_jwt_secret(self, client, app):
        with _service_patch("refresh", return_value=TOKEN_RESPONSE) as mock_refresh, \
             _db_patch():
            client.post(self.URL, json=VALID_REFRESH_PAYLOAD)

        mock_refresh.assert_called_once_with(
            "some-refresh-token",
            app.config["JWT_SECRET_KEY"],
        )
