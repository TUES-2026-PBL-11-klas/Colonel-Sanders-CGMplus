import pytest
from flask import Flask
from flask_smorest import Api


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
        PROPAGATE_EXCEPTIONS=True,
    )

    api = Api(flask_app)
    from src.routes.root import blp
    api.register_blueprint(blp)

    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

class TestRoot:
    def test_returns_redirect(self, client):
        resp = client.get("/")
        assert resp.status_code in (301, 302, 308)

    def test_redirects_to_docs(self, client):
        resp = client.get("/")
        assert resp.headers["Location"].endswith("/docs")

    def test_following_redirect_hits_docs(self, client):
        resp = client.get("/", follow_redirects=False)
        assert "/docs" in resp.headers["Location"]


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_returns_json_content_type(self, client):
        resp = client.get("/health")
        assert resp.content_type == "application/json"

    def test_body_contains_status_ok(self, client):
        resp = client.get("/health")
        assert resp.get_json() == {"status": "ok"}

    def test_post_not_allowed(self, client):
        resp = client.post("/health")
        assert resp.status_code == 405
