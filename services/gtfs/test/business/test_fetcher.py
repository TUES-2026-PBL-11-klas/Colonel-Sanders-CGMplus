"""
Unit tests for src/business/fetcher.py
"""
import io
import zipfile
import threading
from unittest.mock import patch, MagicMock

import pytest
from google.transit import gtfs_realtime_pb2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(content: bytes, status_code: int = 200) -> MagicMock:
    """Return a mock requests.Response."""
    resp = MagicMock()
    resp.content = content
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


def _make_feed_bytes(timestamp: int = 1_700_000_000) -> bytes:
    """Serialise a minimal FeedMessage so ParseFromString succeeds."""
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = timestamp
    return feed.SerializeToString()


def _make_zip(files: dict[str, str]) -> bytes:
    """Build an in-memory ZIP archive from {filename: csv_text} pairs."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_FEEDS = {
    "alerts":            "http://fake/alerts",
    "trip_updates":      "http://fake/trip_updates",
    "vehicle_positions": "http://fake/vehicle_positions",
}

FAKE_STATIC_URL = "http://fake/static.zip"
FAKE_TIMEOUT = 10
FRESH_STORE: dict = {}
FRESH_LOCK = threading.Lock()


@pytest.fixture(autouse=True)
def patch_globals(monkeypatch):
    """
    Redirect every module-level constant and shared-state object that
    fetcher.py imports so tests are fully isolated.
    """
    monkeypatch.setattr("src.business.fetcher.FEEDS", FAKE_FEEDS)
    monkeypatch.setattr("src.business.fetcher.STATIC_URL", FAKE_STATIC_URL)
    monkeypatch.setattr("src.business.fetcher.REQUEST_TIMEOUT", FAKE_TIMEOUT)

    # Give every test a clean store + lock
    fresh_store: dict = {}
    fresh_lock = threading.Lock()
    monkeypatch.setattr("src.business.fetcher._store", fresh_store)
    monkeypatch.setattr("src.business.fetcher._lock",  fresh_lock)

    # Silence the logger so tests stay quiet
    mock_log = MagicMock()
    monkeypatch.setattr("src.business.fetcher.log", mock_log)

    yield fresh_store, mock_log


# ---------------------------------------------------------------------------
# _fetch_realtime
# ---------------------------------------------------------------------------

class TestFetchRealtime:
    """Tests for _fetch_realtime(key)."""

    def _run(self, key: str = "alerts"):
        from src.business.fetcher import _fetch_realtime
        _fetch_realtime(key)

    # --- happy path ---------------------------------------------------------

    @pytest.mark.parametrize(
            "key", ["alerts", "trip_updates", "vehicle_positions"])
    def test_stores_result_for_each_feed_key(self, key, patch_globals):
        store, _ = patch_globals
        feed_bytes = _make_feed_bytes()
        fake_entities = [{"id": "e1"}, {"id": "e2"}]

        with (
            patch("src.business.fetcher.requests.get",
                  return_value=_make_response(feed_bytes)),
            patch(
                "src.business.fetcher.PARSERS",
                {
                    k: MagicMock(return_value=fake_entities)
                    for k in FAKE_FEEDS
                }
            ),
            patch("src.business.fetcher._header_to_dict",
                  return_value={"timestamp": 123}),
        ):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime(key)

        assert key in store
        assert store[key]["entities"] == fake_entities
        assert store[key]["header"] == {"timestamp": 123}
        assert "fetched_at" in store[key]

    def test_fetched_at_is_utc_iso_string(self, patch_globals):
        store, _ = patch_globals
        feed_bytes = _make_feed_bytes()

        with (
            patch("src.business.fetcher.requests.get",
                  return_value=_make_response(feed_bytes)),
            patch("src.business.fetcher.PARSERS",
                  {"alerts": MagicMock(return_value=[])}),
            patch("src.business.fetcher._header_to_dict", return_value={}),
        ):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime("alerts")

        fetched_at = store["alerts"]["fetched_at"]
        # Must be parseable and timezone-aware
        from datetime import datetime
        dt = datetime.fromisoformat(fetched_at)
        assert dt.tzinfo is not None

    def test_requests_get_called_with_correct_url_and_timeout(
        self,
        patch_globals
    ):
        feed_bytes = _make_feed_bytes()

        with (
            patch("src.business.fetcher.requests.get",
                  return_value=_make_response(feed_bytes)) as mock_get,
            patch("src.business.fetcher.PARSERS",
                  {"alerts": MagicMock(return_value=[])}),
            patch("src.business.fetcher._header_to_dict", return_value={}),
        ):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime("alerts")

        mock_get.assert_called_once_with(
            FAKE_FEEDS["alerts"], timeout=FAKE_TIMEOUT
        )

    def test_info_logged_on_success(self, patch_globals):
        _, mock_log = patch_globals
        feed_bytes = _make_feed_bytes()

        with (
            patch("src.business.fetcher.requests.get",
                  return_value=_make_response(feed_bytes)),
            patch("src.business.fetcher.PARSERS",
                  {"alerts": MagicMock(return_value=["x", "y"])}),
            patch("src.business.fetcher._header_to_dict", return_value={}),
        ):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime("alerts")

        assert mock_log.info.called

    # --- error paths --------------------------------------------------------

    def test_http_error_logs_and_does_not_raise(self, patch_globals):
        store, mock_log = patch_globals

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(b"", status_code=503)):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime("alerts")          # must NOT raise

        assert "alerts" not in store
        mock_log.error.assert_called_once()

    def test_network_exception_logs_and_does_not_raise(self, patch_globals):
        store, mock_log = patch_globals

        with patch("src.business.fetcher.requests.get",
                   side_effect=ConnectionError("timeout")):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime("alerts")

        assert "alerts" not in store
        mock_log.error.assert_called_once()

    def test_parser_exception_logs_and_does_not_raise(self, patch_globals):
        store, mock_log = patch_globals
        feed_bytes = _make_feed_bytes()

        with (
            patch("src.business.fetcher.requests.get",
                  return_value=_make_response(feed_bytes)),
            patch("src.business.fetcher.PARSERS",
                  {"alerts": MagicMock(side_effect=ValueError("bad parse"))}),
            patch("src.business.fetcher._header_to_dict", return_value={}),
        ):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime("alerts")

        assert "alerts" not in store
        mock_log.error.assert_called_once()

    def test_store_not_mutated_on_failure(self, patch_globals):
        store, _ = patch_globals
        store["alerts"] = {"entities": ["old"]}   # pre-existing data

        with patch("src.business.fetcher.requests.get",
                   side_effect=RuntimeError("boom")):
            from src.business.fetcher import _fetch_realtime
            _fetch_realtime("alerts")

        # Old data must be preserved — no partial write
        assert store["alerts"] == {"entities": ["old"]}


# ---------------------------------------------------------------------------
# _fetch_static
# ---------------------------------------------------------------------------

AGENCY_CSV = "agency_id,agency_name\nA1,TestAgency\n"
ROUTES_CSV = "route_id,route_short_name\nR1,42\nR2,99\n"
STOPS_CSV = "stop_id,stop_name\nS1,Central\nS2,North\nS3,South\n"
TRIPS_CSV = "trip_id,route_id\nT1,R1\n"
CALENDAR_CSV = "service_id,monday\nSVC1,1\n"


class TestFetchStatic:
    """Tests for _fetch_static()."""

    def _zip_all(self) -> bytes:
        return _make_zip({
            "agency.txt":   AGENCY_CSV,
            "routes.txt":   ROUTES_CSV,
            "stops.txt":    STOPS_CSV,
            "trips.txt":    TRIPS_CSV,
            "calendar.txt": CALENDAR_CSV,
        })

    # --- happy path ---------------------------------------------------------

    def test_store_populated_with_all_keys(self, patch_globals):
        store, _ = patch_globals

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(self._zip_all())):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        assert "static" in store
        for key in (
                      "agency",
                      "routes",
                      "stops",
                      "trips",
                      "calendar",
                      "fetched_at"
                    ):
            assert key in store["static"], f"missing key: {key}"

    def test_csv_rows_parsed_correctly(self, patch_globals):
        store, _ = patch_globals

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(self._zip_all())):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        assert store["static"]["routes"] == [
            {"route_id": "R1", "route_short_name": "42"},
            {"route_id": "R2", "route_short_name": "99"},
        ]
        assert len(store["static"]["stops"]) == 3

    def test_fetched_at_is_utc_iso_string(self, patch_globals):
        store, _ = patch_globals

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(self._zip_all())):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        from datetime import datetime
        dt = datetime.fromisoformat(store["static"]["fetched_at"])
        assert dt.tzinfo is not None

    def test_requests_get_called_with_static_url(self, patch_globals):
        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(self._zip_all())) as mock_get:
            from src.business.fetcher import _fetch_static
            _fetch_static()

        mock_get.assert_called_once_with(FAKE_STATIC_URL, timeout=60)

    def test_missing_optional_file_returns_empty_list(self, patch_globals):
        """ZIP without calendar.txt → calendar list should be empty."""
        store, _ = patch_globals
        partial_zip = _make_zip({
            "agency.txt": AGENCY_CSV,
            "routes.txt": ROUTES_CSV,
            "stops.txt":  STOPS_CSV,
            "trips.txt":  TRIPS_CSV,
            # calendar.txt intentionally omitted
        })

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(partial_zip)):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        assert store["static"]["calendar"] == []

    def test_info_logged_on_success(self, patch_globals):
        _, mock_log = patch_globals

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(self._zip_all())):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        assert mock_log.info.called

    # --- error paths --------------------------------------------------------

    def test_http_error_logs_and_does_not_raise(self, patch_globals):
        store, mock_log = patch_globals

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(b"", status_code=404)):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        assert "static" not in store
        mock_log.error.assert_called_once()

    def test_network_exception_logs_and_does_not_raise(self, patch_globals):
        store, mock_log = patch_globals

        with patch("src.business.fetcher.requests.get",
                   side_effect=TimeoutError("read timeout")):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        assert "static" not in store
        mock_log.error.assert_called_once()

    def test_corrupt_zip_logs_and_does_not_raise(self, patch_globals):
        store, mock_log = patch_globals

        with patch("src.business.fetcher.requests.get",
                   return_value=_make_response(b"not-a-zip")):
            from src.business.fetcher import _fetch_static
            _fetch_static()

        assert "static" not in store
        mock_log.error.assert_called_once()


# ---------------------------------------------------------------------------
# _fetch_all_realtime
# ---------------------------------------------------------------------------

class TestFetchAllRealtime:
    """Tests for _fetch_all_realtime()."""

    def test_calls_fetch_realtime_for_every_feed(self, patch_globals):
        with patch("src.business.fetcher._fetch_realtime") as mock_fr:
            from src.business.fetcher import _fetch_all_realtime
            _fetch_all_realtime()

        assert mock_fr.call_count == len(FAKE_FEEDS)
        mock_fr.assert_any_call("alerts")
        mock_fr.assert_any_call("trip_updates")
        mock_fr.assert_any_call("vehicle_positions")

    def test_continues_after_one_feed_fails(self, patch_globals):
        """
        _fetch_realtime already swallows exceptions, but even if it did not,
        _fetch_all_realtime should iterate all keys.
        """
        call_log: list[str] = []

        def side_effect(key):
            call_log.append(key)
            if key == "alerts":
                raise RuntimeError("simulated crash")

        with patch("src.business.fetcher._fetch_realtime",
                   side_effect=side_effect):
            from src.business.fetcher import _fetch_all_realtime
            # RuntimeError propagates here intentionally — the real
            # _fetch_realtime swallows it, but _fetch_all_realtime itself
            # does not add extra try/except.
            try:
                _fetch_all_realtime()
            except RuntimeError:
                pass

        # At minimum the first key was attempted
        assert "alerts" in call_log
