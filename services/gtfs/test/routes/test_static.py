"""
Unit tests for src/routes/static.py
"""
import pytest
from flask import Flask
from flask_smorest import Api


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

FETCHED_AT = "2024-01-01T00:00:00Z"

SAMPLE_ROUTES = [
    {"route_id": "R1", "route_short_name": "1",  "route_long_name": "Main Line"},
    {"route_id": "R2", "route_short_name": "2",  "route_long_name": "Cross Town"},
    {"route_id": "R3", "route_short_name": "10", "route_long_name": "Express"},
]

SAMPLE_STOPS = [
    {"stop_id": "S1", "stop_name": "Central Station", "stop_lat": 42.0, "stop_lon": -71.0},
    {"stop_id": "S2", "stop_name": "North Stop",      "stop_lat": 42.1, "stop_lon": -71.1},
    {"stop_id": "S3", "stop_name": "South Stop",      "stop_lat": 41.9, "stop_lon": -71.2},
]

SAMPLE_TRIPS = [
    {"trip_id": "T1", "route_id": "R1", "service_id": "WD"},
    {"trip_id": "T2", "route_id": "R1", "service_id": "WE"},
    {"trip_id": "T3", "route_id": "R2", "service_id": "WD"},
]

SAMPLE_AGENCY = [{"agency_id": "A1", "agency_name": "Transit Co."}]
SAMPLE_CALENDAR = [{"service_id": "WD", "monday": 1, "sunday": 0}]

FULL_SNAPSHOT = {
    "fetched_at": FETCHED_AT,
    "routes":     SAMPLE_ROUTES,
    "stops":      SAMPLE_STOPS,
    "trips":      SAMPLE_TRIPS,
    "agency":     SAMPLE_AGENCY,
    "calendar":   SAMPLE_CALENDAR,
}


@pytest.fixture()
def app():
    """Minimal Flask + flask-smorest app with the static blueprint registered."""
    flask_app = Flask(__name__)
    flask_app.config["API_TITLE"] = "Test"
    flask_app.config["API_VERSION"] = "v1"
    flask_app.config["OPENAPI_VERSION"] = "3.0.3"
    flask_app.config["TESTING"] = True

    api = Api(flask_app)

    # Import blueprint here so the patch target is always the module-level symbol
    from src.routes.static import blp
    api.register_blueprint(blp)

    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_snapshot(monkeypatch):
    """Patch _snapshot for every test so no real store is needed."""
    monkeypatch.setattr(
        "src.routes.static._snapshot",
        lambda _feed: dict(FULL_SNAPSHOT),   # fresh copy each call
    )


# ---------------------------------------------------------------------------
# _paginate (pure-function tests – no HTTP overhead)
# ---------------------------------------------------------------------------

class TestPaginate:
    from src.routes.static import _paginate  # import once for the class

    def test_first_page(self):
        from src.routes.static import _paginate
        result = _paginate(list(range(10)), page=1, per_page=3)
        assert result["items"] == [0, 1, 2]
        assert result["total"] == 10
        assert result["pages"] == 4
        assert result["page"] == 1
        assert result["per_page"] == 3

    def test_last_partial_page(self):
        from src.routes.static import _paginate
        result = _paginate(list(range(10)), page=4, per_page=3)
        assert result["items"] == [9]

    def test_beyond_last_page_returns_empty(self):
        from src.routes.static import _paginate
        result = _paginate(list(range(5)), page=99, per_page=10)
        assert result["items"] == []

    def test_empty_list(self):
        from src.routes.static import _paginate
        result = _paginate([], page=1, per_page=10)
        assert result["items"] == []
        assert result["total"] == 0
        assert result["pages"] == 0

    def test_exact_page_boundary(self):
        from src.routes.static import _paginate
        result = _paginate(list(range(9)), page=3, per_page=3)
        assert result["items"] == [6, 7, 8]
        assert result["pages"] == 3


# ---------------------------------------------------------------------------
# GET /static/routes
# ---------------------------------------------------------------------------

class TestStaticRoutes:

    def test_returns_all_routes(self, client):
        resp = client.get("/static/routes")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["fetched_at"] == FETCHED_AT
        assert len(body["routes"]) == len(SAMPLE_ROUTES)

    def test_pagination_structure_present(self, client):
        resp = client.get("/static/routes")
        body = resp.get_json()
        for key in ("total", "page", "per_page", "pages"):
            assert key in body["pagination"]

    def test_search_by_route_short_name(self, client):
        resp = client.get("/static/routes?q=1")
        body = resp.get_json()
        # "1" matches route_short_name "1" and "10"
        names = [r["route_short_name"] for r in body["routes"]]
        assert all("1" in n for n in names)

    def test_search_no_match_returns_empty(self, client):
        resp = client.get("/static/routes?q=zzznomatch")
        body = resp.get_json()
        assert body["routes"] == []

    def test_pagination_per_page(self, client):
        resp = client.get("/static/routes?per_page=1&page=1")
        body = resp.get_json()
        assert len(body["routes"]) == 1
        assert body["pagination"]["per_page"] == 1

    def test_per_page_capped_at_500(self, client):
        resp = client.get("/static/routes?per_page=9999")
        body = resp.get_json()
        assert body["pagination"]["per_page"] == 500

    def test_per_page_minimum_is_1(self, client):
        resp = client.get("/static/routes?per_page=0")
        body = resp.get_json()
        assert body["pagination"]["per_page"] == 1

    def test_page_minimum_is_1(self, client):
        resp = client.get("/static/routes?page=-5")
        body = resp.get_json()
        assert body["pagination"]["page"] == 1


# ---------------------------------------------------------------------------
# GET /static/routes/<route_id>
# ---------------------------------------------------------------------------

class TestStaticRoute:

    def test_returns_known_route(self, client):
        resp = client.get("/static/routes/R1")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["route"]["route_id"] == "R1"
        assert body["fetched_at"] == FETCHED_AT

    def test_unknown_route_returns_404(self, client):
        resp = client.get("/static/routes/DOES_NOT_EXIST")
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body


# ---------------------------------------------------------------------------
# GET /static/stops
# ---------------------------------------------------------------------------

class TestStaticStops:

    def test_returns_all_stops(self, client):
        resp = client.get("/static/stops")
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["stops"]) == len(SAMPLE_STOPS)

    def test_search_by_stop_name(self, client):
        resp = client.get("/static/stops?q=north")
        body = resp.get_json()
        assert len(body["stops"]) == 1
        assert body["stops"][0]["stop_id"] == "S2"

    def test_search_case_insensitive(self, client):
        resp = client.get("/static/stops?q=CENTRAL")
        body = resp.get_json()
        assert len(body["stops"]) == 1

    def test_pagination_second_page(self, client):
        resp = client.get("/static/stops?per_page=2&page=2")
        body = resp.get_json()
        assert len(body["stops"]) == 1  # 3 stops total → page 2 has 1


# ---------------------------------------------------------------------------
# GET /static/stops/<stop_id>
# ---------------------------------------------------------------------------

class TestStaticStop:

    def test_returns_known_stop(self, client):
        resp = client.get("/static/stops/S1")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["stop"]["stop_id"] == "S1"

    def test_unknown_stop_returns_404(self, client):
        resp = client.get("/static/stops/NOPE")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


# ---------------------------------------------------------------------------
# GET /static/trips
# ---------------------------------------------------------------------------

class TestStaticTrips:

    def test_returns_all_trips_without_filter(self, client):
        resp = client.get("/static/trips")
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["trips"]) == len(SAMPLE_TRIPS)

    def test_filter_by_route_id(self, client):
        resp = client.get("/static/trips?route_id=R1")
        body = resp.get_json()
        assert all(t["route_id"] == "R1" for t in body["trips"])
        assert len(body["trips"]) == 2

    def test_filter_unknown_route_returns_empty(self, client):
        resp = client.get("/static/trips?route_id=UNKNOWN")
        body = resp.get_json()
        assert body["trips"] == []

    def test_pagination_present(self, client):
        resp = client.get("/static/trips")
        body = resp.get_json()
        assert "pagination" in body

    def test_fetched_at_in_response(self, client):
        resp = client.get("/static/trips")
        assert resp.get_json()["fetched_at"] == FETCHED_AT


# ---------------------------------------------------------------------------
# GET /static/agency
# ---------------------------------------------------------------------------

class TestStaticAgency:

    def test_returns_agency(self, client):
        resp = client.get("/static/agency")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["agency"] == SAMPLE_AGENCY
        assert body["fetched_at"] == FETCHED_AT


# ---------------------------------------------------------------------------
# GET /static/calendar
# ---------------------------------------------------------------------------

class TestStaticCalendar:

    def test_returns_calendar(self, client):
        resp = client.get("/static/calendar")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["calendar"] == SAMPLE_CALENDAR
        assert body["fetched_at"] == FETCHED_AT


# ---------------------------------------------------------------------------
# Edge-cases / snapshot with missing keys
# ---------------------------------------------------------------------------

class TestMissingSnapshotKeys:

    def test_routes_missing_key_returns_empty(self, client, monkeypatch):
        monkeypatch.setattr(
            "src.routes.static._snapshot",
            lambda _: {"fetched_at": FETCHED_AT},  # no "routes" key
        )
        resp = client.get("/static/routes")
        body = resp.get_json()
        assert body["routes"] == []

    def test_stops_missing_key_returns_empty(self, client, monkeypatch):
        monkeypatch.setattr(
            "src.routes.static._snapshot",
            lambda _: {"fetched_at": FETCHED_AT},
        )
        resp = client.get("/static/stops")
        body = resp.get_json()
        assert body["stops"] == []

    def test_trips_missing_key_returns_empty(self, client, monkeypatch):
        monkeypatch.setattr(
            "src.routes.static._snapshot",
            lambda _: {"fetched_at": FETCHED_AT},
        )
        resp = client.get("/static/trips")
        body = resp.get_json()
        assert body["trips"] == []
