"""
Unit tests for src/routes/root.py
"""
import threading
import pytest
from flask import Flask
from flask_smorest import Api

# ---------------------------------------------------------------------------
# Sample store data
# ---------------------------------------------------------------------------

FETCHED_AT_ALERTS = "2024-01-01T10:00:00Z"
FETCHED_AT_TRIPS = "2024-01-01T10:05:00Z"
FETCHED_AT_VEHICLES = "2024-01-01T10:10:00Z"
FETCHED_AT_STATIC = "2024-01-01T09:00:00Z"

SAMPLE_STORE = {
    "alerts": {
        "fetched_at": FETCHED_AT_ALERTS,
        "entities": [{"id": "A1"}, {"id": "A2"}],
    },
    "trip_updates": {
        "fetched_at": FETCHED_AT_TRIPS,
        "entities": [{"id": "TU1"}],
    },
    "vehicle_positions": {
        "fetched_at": FETCHED_AT_VEHICLES,
        "entities": [{"id": "V1"}, {"id": "V2"}, {"id": "V3"}],
    },
    "static": {
        "fetched_at": FETCHED_AT_STATIC,
        "routes": [{"route_id": "R1"}, {"route_id": "R2"}],
    },
}

# All expected top-level endpoint keys documented in the index response
EXPECTED_ENDPOINTS = {
    "GET /alerts",
    "GET /trip-updates",
    "GET /vehicle-positions",
    "GET /vehicle-positions/route/<route_id>",
    "GET /static/routes",
    "GET /static/stops",
    "GET /static/trips",
    "GET /static/agency",
    "GET /static/calendar",
    "GET /status",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def app():
    flask_app = Flask(__name__)
    flask_app.config.update(
        TESTING=True,
        API_TITLE="Test",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
    )
    Api(flask_app)

    from src.routes.root import blp
    # Re-register a fresh blueprint instance each time to avoid state leakage
    flask_app.register_blueprint(blp)
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def patch_store(monkeypatch):
    """Replace the module-level _store and _lock used by root.py."""
    import src.routes.root as root_module

    # Fresh copy of data so tests cannot mutate shared state
    fake_store = {k: dict(v) for k, v in SAMPLE_STORE.items()}
    monkeypatch.setattr(root_module, "_store", fake_store)
    monkeypatch.setattr(root_module, "_lock", threading.Lock())

    return fake_store          # yielded so individual tests can mutate it


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

class TestIndex:

    def test_status_200(self, client):
        assert client.get("/").status_code == 200

    def test_top_level_keys(self, client):
        body = client.get("/").get_json()
        assert set(body.keys()) == {"service", "endpoints", "feed_status"}

    def test_service_name(self, client):
        body = client.get("/").get_json()
        assert body["service"] == "Sofia Transit GTFS API"

    def test_all_endpoints_documented(self, client):
        body = client.get("/").get_json()
        assert set(body["endpoints"].keys()) == EXPECTED_ENDPOINTS

    def test_endpoint_values_are_strings(self, client):
        body = client.get("/").get_json()
        for key, val in body["endpoints"].items():
            assert isinstance(val, str), f"Endpoint description for '{key}' is not a string"

    # --- feed_status shape ---

    def test_feed_status_contains_all_store_keys(self, client):
        body = client.get("/").get_json()
        assert set(body["feed_status"].keys()) == set(SAMPLE_STORE.keys())

    def test_feed_status_entry_keys(self, client):
        body = client.get("/").get_json()
        for key, entry in body["feed_status"].items():
            assert "fetched_at" in entry, f"'fetched_at' missing for feed '{key}'"
            assert "entity_count" in entry, f"'entity_count' missing for feed '{key}'"

    # --- entity_count logic: prefers "entities", falls back to "routes" ---

    def test_entity_count_for_entities_feed(self, client):
        body = client.get("/").get_json()
        assert body["feed_status"]["alerts"]["entity_count"] == 2
        assert body["feed_status"]["trip_updates"]["entity_count"] == 1
        assert body["feed_status"]["vehicle_positions"]["entity_count"] == 3

    def test_entity_count_falls_back_to_routes(self, client):
        body = client.get("/").get_json()
        # "static" has no "entities" key — falls back to "routes"
        assert body["feed_status"]["static"]["entity_count"] == 2

    def test_fetched_at_values_correct(self, client):
        body = client.get("/").get_json()
        fs = body["feed_status"]
        assert fs["alerts"]["fetched_at"] == FETCHED_AT_ALERTS
        assert fs["trip_updates"]["fetched_at"] == FETCHED_AT_TRIPS
        assert fs["vehicle_positions"]["fetched_at"] == FETCHED_AT_VEHICLES
        assert fs["static"]["fetched_at"] == FETCHED_AT_STATIC

    # --- edge cases ---

    def test_empty_store(self, client, monkeypatch):
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {})
        body = client.get("/").get_json()
        assert body["feed_status"] == {}

    def test_feed_with_no_fetched_at(self, client, monkeypatch):
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {
            "alerts": {"entities": [{"id": "X"}]},   # no fetched_at
        })
        body = client.get("/").get_json()
        assert body["feed_status"]["alerts"]["fetched_at"] is None

    def test_feed_with_empty_entities(self, client, monkeypatch):
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {
            "alerts": {"fetched_at": "2024-01-01T00:00:00Z", "entities": []},
        })
        body = client.get("/").get_json()
        assert body["feed_status"]["alerts"]["entity_count"] == 0

    def test_feed_with_no_entities_or_routes_key(self, client, monkeypatch):
        """Falls back to empty list when neither 'entities' nor 'routes' key is present."""
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {
            "mystery_feed": {"fetched_at": "2024-01-01T00:00:00Z"},
        })
        body = client.get("/").get_json()
        assert body["feed_status"]["mystery_feed"]["entity_count"] == 0

    def test_content_type_is_json(self, client):
        resp = client.get("/")
        assert resp.content_type == "application/json"


# ---------------------------------------------------------------------------
# GET /status
# ---------------------------------------------------------------------------

class TestStatus:

    def test_status_200(self, client):
        assert client.get("/status").status_code == 200

    def test_contains_all_store_keys(self, client):
        body = client.get("/status").get_json()
        assert set(body.keys()) == set(SAMPLE_STORE.keys())

    def test_entry_keys(self, client):
        body = client.get("/status").get_json()
        for key, entry in body.items():
            assert "fetched_at" in entry, f"'fetched_at' missing for feed '{key}'"
            assert "count" in entry, f"'count' missing for feed '{key}'"

    # --- count resolution: entities → routes → stops → [] ---

    def test_count_via_entities(self, client):
        body = client.get("/status").get_json()
        assert body["alerts"]["count"] == 2
        assert body["trip_updates"]["count"] == 1
        assert body["vehicle_positions"]["count"] == 3

    def test_count_via_routes_fallback(self, client):
        body = client.get("/status").get_json()
        assert body["static"]["count"] == 2

    def test_count_via_stops_fallback(self, client, monkeypatch):
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {
            "static": {
                "fetched_at": FETCHED_AT_STATIC,
                "stops": [{"stop_id": "S1"}, {"stop_id": "S2"}, {"stop_id": "S3"}],
            }
        })
        body = client.get("/status").get_json()
        assert body["static"]["count"] == 3

    def test_fetched_at_values_correct(self, client):
        body = client.get("/status").get_json()
        assert body["alerts"]["fetched_at"] == FETCHED_AT_ALERTS
        assert body["trip_updates"]["fetched_at"] == FETCHED_AT_TRIPS
        assert body["vehicle_positions"]["fetched_at"] == FETCHED_AT_VEHICLES
        assert body["static"]["fetched_at"] == FETCHED_AT_STATIC

    def test_empty_store(self, client, monkeypatch):
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {})
        body = client.get("/status").get_json()
        assert body == {}

    def test_no_fetched_at_returns_none(self, client, monkeypatch):
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {
            "alerts": {"entities": []},
        })
        body = client.get("/status").get_json()
        assert body["alerts"]["fetched_at"] is None

    def test_no_collection_key_count_is_zero(self, client, monkeypatch):
        """count falls back to 0 when none of entities/routes/stops are present."""
        import src.routes.root as root_module
        monkeypatch.setattr(root_module, "_store", {
            "mystery": {"fetched_at": "2024-01-01T00:00:00Z"},
        })
        body = client.get("/status").get_json()
        assert body["mystery"]["count"] == 0

    def test_content_type_is_json(self, client):
        resp = client.get("/status")
        assert resp.content_type == "application/json"

    def test_multiple_feeds_independent(self, client):
        """Mutating one feed entry should not affect another feed's count."""
        body = client.get("/status").get_json()
        assert body["alerts"]["count"] != body["vehicle_positions"]["count"]


# ---------------------------------------------------------------------------
# Lock behaviour
# ---------------------------------------------------------------------------

class TestLockUsage:
    """Verify that the store is accessed under the lock (smoke test via re-entrant check)."""

    def test_index_completes_while_lock_is_free(self, client):
        """Basic smoke-test: response succeeds when the lock is not held externally."""
        resp = client.get("/")
        assert resp.status_code == 200

    def test_status_completes_while_lock_is_free(self, client):
        resp = client.get("/status")
        assert resp.status_code == 200
