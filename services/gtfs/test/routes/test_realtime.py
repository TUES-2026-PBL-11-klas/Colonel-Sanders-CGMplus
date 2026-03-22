"""
Unit tests for src/routes/realtime.py
"""
import pytest
from flask import Flask
from flask_smorest import Api

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

FETCHED_AT = "2024-01-01T12:00:00Z"
SAMPLE_HEADER = {"gtfs_realtime_version": "2.0", "timestamp": 1704067200}

SAMPLE_ALERTS = [
    {"id": "A1", "alert": {"header_text": "Delay on Line 1"}},
    {"id": "A2", "alert": {"header_text": "Service suspended"}},
]

SAMPLE_TRIP_UPDATES = [
    {"id": "TU1", "trip": {"trip_id": "T1", "route_id": "R1"}, "stop_time_updates": []},
    {"id": "TU2", "trip": {"trip_id": "T2", "route_id": "R2"}, "stop_time_updates": []},
    {"id": "TU3", "trip": {"trip_id": "T3", "route_id": "R1"}, "stop_time_updates": []},
    {"id": "TU4", "trip": None, "stop_time_updates": []},   # no trip field edge-case
]

SAMPLE_VEHICLE_POSITIONS = [
    {"id": "V1", "trip": {"trip_id": "T1", "route_id": "R1"}, "position": {"lat": 42.0, "lon": -71.0}},
    {"id": "V2", "trip": {"trip_id": "T2", "route_id": "R2"}, "position": {"lat": 42.1, "lon": -71.1}},
    {"id": "V3", "trip": {"trip_id": "T3", "route_id": "R1"}, "position": {"lat": 42.2, "lon": -71.2}},
    {"id": "V4", "trip": None,                                 "position": {"lat": 0.0,  "lon": 0.0}},  # no trip
]

SNAPSHOTS = {
    "alerts": {
        "fetched_at": FETCHED_AT,
        "header":     SAMPLE_HEADER,
        "entities":   SAMPLE_ALERTS,
    },
    "trip_updates": {
        "fetched_at": FETCHED_AT,
        "header":     SAMPLE_HEADER,
        "entities":   SAMPLE_TRIP_UPDATES,
    },
    "vehicle_positions": {
        "fetched_at": FETCHED_AT,
        "header":     SAMPLE_HEADER,
        "entities":   SAMPLE_VEHICLE_POSITIONS,
    },
}


def _make_snapshot(feed: str) -> dict:
    """Return a deep-enough copy so tests cannot mutate shared state."""
    snap = SNAPSHOTS[feed]
    return {**snap, "entities": list(snap["entities"])}


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
    api = Api(flask_app)
    from src.routes.realtime import blp
    api.register_blueprint(blp)
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_snapshot(monkeypatch):
    monkeypatch.setattr("src.routes.realtime._snapshot", _make_snapshot)


# ---------------------------------------------------------------------------
# GET /alerts
# ---------------------------------------------------------------------------

class TestAlerts:

    def test_status_200(self, client):
        assert client.get("/alerts").status_code == 200

    def test_response_keys(self, client):
        body = client.get("/alerts").get_json()
        assert set(body.keys()) == {"fetched_at", "header", "count", "alerts"}

    def test_fetched_at(self, client):
        body = client.get("/alerts").get_json()
        assert body["fetched_at"] == FETCHED_AT

    def test_header(self, client):
        body = client.get("/alerts").get_json()
        assert body["header"] == SAMPLE_HEADER

    def test_count_matches_entities(self, client):
        body = client.get("/alerts").get_json()
        assert body["count"] == len(SAMPLE_ALERTS)
        assert body["count"] == len(body["alerts"])

    def test_alerts_payload(self, client):
        body = client.get("/alerts").get_json()
        ids = [a["id"] for a in body["alerts"]]
        assert ids == ["A1", "A2"]

    def test_empty_alerts(self, client, monkeypatch):
        monkeypatch.setattr(
            "src.routes.realtime._snapshot",
            lambda _: {"fetched_at": FETCHED_AT, "header": SAMPLE_HEADER, "entities": []},
        )
        body = client.get("/alerts").get_json()
        assert body["count"] == 0
        assert body["alerts"] == []


# ---------------------------------------------------------------------------
# GET /trip-updates
# ---------------------------------------------------------------------------

class TestTripUpdates:

    def test_status_200(self, client):
        assert client.get("/trip-updates").status_code == 200

    def test_response_keys(self, client):
        body = client.get("/trip-updates").get_json()
        assert set(body.keys()) == {"fetched_at", "header", "count", "trip_updates"}

    def test_returns_all_without_filter(self, client):
        body = client.get("/trip-updates").get_json()
        assert body["count"] == len(SAMPLE_TRIP_UPDATES)
        assert len(body["trip_updates"]) == body["count"]

    def test_filter_by_route_id(self, client):
        body = client.get("/trip-updates?route_id=R1").get_json()
        assert body["count"] == 2
        route_ids = [e["trip"]["route_id"] for e in body["trip_updates"]]
        assert all(r == "R1" for r in route_ids)

    def test_filter_unknown_route_returns_empty(self, client):
        body = client.get("/trip-updates?route_id=UNKNOWN").get_json()
        assert body["count"] == 0
        assert body["trip_updates"] == []

    def test_entities_with_none_trip_excluded_when_filtered(self, client):
        """Entities where trip is None/falsy must be excluded by the route_id filter."""
        body = client.get("/trip-updates?route_id=R1").get_json()
        ids = [e["id"] for e in body["trip_updates"]]
        assert "TU4" not in ids  # TU4 has trip=None

    def test_entities_with_none_trip_included_without_filter(self, client):
        """Entities with trip=None should still appear when no filter is applied."""
        body = client.get("/trip-updates").get_json()
        ids = [e["id"] for e in body["trip_updates"]]
        assert "TU4" in ids

    def test_count_equals_entity_length(self, client):
        body = client.get("/trip-updates?route_id=R2").get_json()
        assert body["count"] == len(body["trip_updates"])

    def test_fetched_at_and_header(self, client):
        body = client.get("/trip-updates").get_json()
        assert body["fetched_at"] == FETCHED_AT
        assert body["header"] == SAMPLE_HEADER


# ---------------------------------------------------------------------------
# GET /vehicle-positions
# ---------------------------------------------------------------------------

class TestVehiclePositions:

    def test_status_200(self, client):
        assert client.get("/vehicle-positions").status_code == 200

    def test_response_keys(self, client):
        body = client.get("/vehicle-positions").get_json()
        assert set(body.keys()) == {"fetched_at", "header", "count", "vehicle_positions"}

    def test_returns_all_without_filter(self, client):
        body = client.get("/vehicle-positions").get_json()
        assert body["count"] == len(SAMPLE_VEHICLE_POSITIONS)

    def test_filter_by_route_id(self, client):
        body = client.get("/vehicle-positions?route_id=R1").get_json()
        assert body["count"] == 2
        ids = [e["id"] for e in body["vehicle_positions"]]
        assert set(ids) == {"V1", "V3"}

    def test_filter_unknown_route_returns_empty(self, client):
        body = client.get("/vehicle-positions?route_id=NOPE").get_json()
        assert body["count"] == 0
        assert body["vehicle_positions"] == []

    def test_none_trip_excluded_when_filtered(self, client):
        body = client.get("/vehicle-positions?route_id=R2").get_json()
        ids = [e["id"] for e in body["vehicle_positions"]]
        assert "V4" not in ids

    def test_none_trip_included_without_filter(self, client):
        body = client.get("/vehicle-positions").get_json()
        ids = [e["id"] for e in body["vehicle_positions"]]
        assert "V4" in ids

    def test_count_equals_entity_length(self, client):
        body = client.get("/vehicle-positions?route_id=R1").get_json()
        assert body["count"] == len(body["vehicle_positions"])

    def test_fetched_at_and_header(self, client):
        body = client.get("/vehicle-positions").get_json()
        assert body["fetched_at"] == FETCHED_AT
        assert body["header"] == SAMPLE_HEADER

    def test_empty_positions(self, client, monkeypatch):
        monkeypatch.setattr(
            "src.routes.realtime._snapshot",
            lambda _: {"fetched_at": FETCHED_AT, "header": SAMPLE_HEADER, "entities": []},
        )
        body = client.get("/vehicle-positions").get_json()
        assert body["count"] == 0
        assert body["vehicle_positions"] == []


# ---------------------------------------------------------------------------
# GET /vehicle-positions/route/<route_id>
# ---------------------------------------------------------------------------

class TestVehiclePositionsByRoute:

    def test_status_200_known_route(self, client):
        assert client.get("/vehicle-positions/route/R1").status_code == 200

    def test_response_keys(self, client):
        body = client.get("/vehicle-positions/route/R1").get_json()
        assert set(body.keys()) == {"fetched_at", "route_id", "count", "vehicle_positions"}

    def test_route_id_echoed_in_response(self, client):
        body = client.get("/vehicle-positions/route/R2").get_json()
        assert body["route_id"] == "R2"

    def test_returns_correct_vehicles_for_route(self, client):
        body = client.get("/vehicle-positions/route/R1").get_json()
        assert body["count"] == 2
        ids = {e["id"] for e in body["vehicle_positions"]}
        assert ids == {"V1", "V3"}

    def test_returns_single_vehicle_for_r2(self, client):
        body = client.get("/vehicle-positions/route/R2").get_json()
        assert body["count"] == 1
        assert body["vehicle_positions"][0]["id"] == "V2"

    def test_unknown_route_returns_empty_not_404(self, client):
        """The endpoint returns 200 with an empty list for unknown routes."""
        resp = client.get("/vehicle-positions/route/UNKNOWN")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["count"] == 0
        assert body["vehicle_positions"] == []
        assert body["route_id"] == "UNKNOWN"

    def test_none_trip_vehicles_excluded(self, client):
        """V4 has trip=None and must never appear in a route-filtered response."""
        body = client.get("/vehicle-positions/route/R1").get_json()
        ids = [e["id"] for e in body["vehicle_positions"]]
        assert "V4" not in ids

    def test_count_equals_entity_length(self, client):
        body = client.get("/vehicle-positions/route/R1").get_json()
        assert body["count"] == len(body["vehicle_positions"])

    def test_fetched_at_present(self, client):
        body = client.get("/vehicle-positions/route/R1").get_json()
        assert body["fetched_at"] == FETCHED_AT

    def test_route_id_with_special_characters(self, client):
        """Route IDs may contain hyphens or underscores – the path param should pass through."""
        body = client.get("/vehicle-positions/route/route-99_express").get_json()
        assert body["route_id"] == "route-99_express"
        assert body["count"] == 0
