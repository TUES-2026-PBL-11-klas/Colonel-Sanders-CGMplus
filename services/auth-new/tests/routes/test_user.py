import uuid
from unittest.mock import MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# Minimal Flask app wiring for route tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    """
    Build a minimal Flask + flask-smorest app that registers only the user
    blueprint.  All heavy dependencies (DB, JWT internals) are patched at
    import time so we never touch a real database.
    """
    from flask import Flask
    from flask_smorest import Api
    from flask_jwt_extended import JWTManager

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

    from src.routes.user import blp
    api.register_blueprint(blp, url_prefix="/users")

    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

USER_ID = uuid.uuid4()
USER_EMAIL = "user@example.com"
HASHED_PW = "$2b$12$hashedvalue"


def _make_user(*, is_active=True, hashed_password=HASHED_PW):
    user = MagicMock()
    user.id = USER_ID
    user.email = USER_EMAIL
    user.is_active = is_active
    user.hashed_password = hashed_password
    return user


def _jwt_patch(identity: str = str(USER_ID)):
    """Patch get_jwt_identity to return *identity* and skip JWT verification."""
    return patch("src.routes.user.get_jwt_identity", return_value=identity)


def _repo_patch(mock_repo: MagicMock):
    return patch("src.routes.user.UserRepository", return_value=mock_repo)


def _auth_headers():
    """Dummy Authorization header — JWT verification is patched away."""
    return {"Authorization": "Bearer dummy"}


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------

class TestUserMeGet:
    URL = "/users/me"

    def test_returns_200_and_email(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.get(self.URL, headers=_auth_headers())

        assert resp.status_code == 200
        assert resp.get_json()["email"] == USER_EMAIL

    def test_returns_404_when_user_not_found(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = None

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.get(self.URL, headers=_auth_headers())

        assert resp.status_code == 404

    def test_returns_403_when_user_inactive(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user(is_active=False)

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.get(self.URL, headers=_auth_headers())

        assert resp.status_code == 403

    def test_returns_400_on_invalid_uuid_identity(self, client):
        repo = MagicMock()

        with _jwt_patch(identity="not-a-uuid"), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.get(self.URL, headers=_auth_headers())

        assert resp.status_code == 400

    def test_repo_queried_with_correct_uuid(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            client.get(self.URL, headers=_auth_headers())

        repo.get_by_id.assert_called_once_with(USER_ID)


# ---------------------------------------------------------------------------
# DELETE /users/me
# ---------------------------------------------------------------------------

class TestUserMeDelete:
    URL = "/users/me"

    def test_returns_204_on_success(self, client):
        repo = MagicMock()
        repo.deactivate.return_value = MagicMock()  # truthy = found

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.db") as mock_db:
            resp = client.delete(self.URL, headers=_auth_headers())

        assert resp.status_code == 204

    def test_commits_session_on_success(self, client):
        repo = MagicMock()
        repo.deactivate.return_value = MagicMock()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.db") as mock_db:
            client.delete(self.URL, headers=_auth_headers())

        mock_db.session.commit.assert_called_once()

    def test_returns_404_when_user_not_found(self, client):
        repo = MagicMock()
        repo.deactivate.return_value = None  # user not found

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.delete(self.URL, headers=_auth_headers())

        assert resp.status_code == 404

    def test_returns_400_on_invalid_uuid_identity(self, client):
        repo = MagicMock()

        with _jwt_patch(identity="bad-uuid"), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.delete(self.URL, headers=_auth_headers())

        assert resp.status_code == 400

    def test_deactivate_called_with_correct_uuid(self, client):
        repo = MagicMock()
        repo.deactivate.return_value = MagicMock()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.db"):
            client.delete(self.URL, headers=_auth_headers())

        repo.deactivate.assert_called_once_with(USER_ID)


# ---------------------------------------------------------------------------
# PATCH /users/me/password
# ---------------------------------------------------------------------------

VALID_PW_PAYLOAD = {
    "current_password": "OldPass1!",
    "new_password": "NewPass2@",
}


class TestChangePasswordPatch:
    URL = "/users/me/password"

    def test_returns_204_on_success(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.SecurityService.check_password", return_value=True), \
             patch("src.routes.user.SecurityService.hash_password", return_value="new-hash"), \
             patch("src.routes.user.db") as mock_db:
            resp = client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        assert resp.status_code == 204

    def test_commits_session_on_success(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.SecurityService.check_password", return_value=True), \
             patch("src.routes.user.SecurityService.hash_password", return_value="new-hash"), \
             patch("src.routes.user.db") as mock_db:
            client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        mock_db.session.commit.assert_called_once()

    def test_clears_tokens_on_success(self, client):
        repo = MagicMock()
        user = _make_user()
        repo.get_by_id.return_value = user

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.SecurityService.check_password", return_value=True), \
             patch("src.routes.user.SecurityService.hash_password", return_value="new-hash"), \
             patch("src.routes.user.db"):
            client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        repo.update.assert_called_once_with(
            user,
            hashed_password="new-hash",
            access_jwt=None,
            refresh_jwt=None,
        )

    def test_returns_401_when_current_password_wrong(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.SecurityService.check_password", return_value=False):
            resp = client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        assert resp.status_code == 401

    def test_returns_404_when_user_not_found(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = None

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        assert resp.status_code == 404

    def test_returns_403_when_user_inactive(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user(is_active=False)

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        assert resp.status_code == 403

    def test_returns_400_on_invalid_uuid_identity(self, client):
        repo = MagicMock()

        with _jwt_patch(identity="not-a-uuid"), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        assert resp.status_code == 400

    def test_returns_422_on_invalid_request_body(self, client):
        """flask-smorest validates the schema before calling the view."""
        with _jwt_patch(), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"):
            resp = client.patch(
                self.URL,
                json={"current_password": "only-one-field"},
                headers=_auth_headers(),
            )

        assert resp.status_code == 422

    def test_does_not_commit_when_current_password_wrong(self, client):
        repo = MagicMock()
        repo.get_by_id.return_value = _make_user()

        with _jwt_patch(), _repo_patch(repo), \
             patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
             patch("src.routes.user.SecurityService.check_password", return_value=False), \
             patch("src.routes.user.db") as mock_db:
            client.patch(self.URL, json=VALID_PW_PAYLOAD, headers=_auth_headers())

        mock_db.session.commit.assert_not_called()
