from ..config import FEEDS, STATIC_URL, REQUEST_TIMEOUT
from .store import _store, _lock
# from ..util.logging import *
from ..util.logging import log
import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime, timezone
import zipfile
import io
import csv

from ..util.gtfs import _header_to_dict

from ..parser.alerts import _parse_alerts
from ..parser.trip_updates import _parse_trip_updates
from ..parser.vehicle_positions import _parse_vehicle_positions

PARSERS = {
    "alerts":            _parse_alerts,
    "trip_updates":      _parse_trip_updates,
    "vehicle_positions": _parse_vehicle_positions,
}


def _fetch_realtime(key: str):
    url = FEEDS[key]
    try:
        log.info("Fetching %s …", key)
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)

        entities = PARSERS[key](feed)
        header = _header_to_dict(feed.header)
        now_iso = datetime.now(tz=timezone.utc).isoformat()

        with _lock:
            _store[key] = {
                "fetched_at": now_iso,
                "header":     header,
                "entities":   entities,
            }
        log.info("Updated %s — %d entities", key, len(entities))

    except Exception as exc:
        log.error("Failed to fetch %s: %s", key, exc)


def _fetch_static():
    try:
        log.info("Fetching static GTFS …")
        resp = requests.get(STATIC_URL, timeout=60)
        resp.raise_for_status()

        z = zipfile.ZipFile(io.BytesIO(resp.content))

        def _read(name: str) -> list[dict]:
            if name not in z.namelist():
                return []
            with z.open(name) as f:
                reader = csv.DictReader(
                    io.TextIOWrapper(
                        f,
                        encoding="utf-8-sig"
                    )
                )
                return [dict(row) for row in reader]

        agency = _read("agency.txt")
        routes = _read("routes.txt")
        stops = _read("stops.txt")
        trips = _read("trips.txt")
        calendar = _read("calendar.txt")

        now_iso = datetime.now(tz=timezone.utc).isoformat()
        with _lock:
            _store["static"] = {
                "fetched_at": now_iso,
                "agency":     agency,
                "routes":     routes,
                "stops":      stops,
                "trips":      trips,
                "calendar":   calendar,
            }
        log.info(
            "Updated static — %d routes, %d stops, %d trips",
            len(routes), len(stops), len(trips),
        )
    except Exception as exc:
        log.error("Failed to fetch static GTFS: %s", exc)


def _fetch_all_realtime():
    for key in FEEDS:
        _fetch_realtime(key)
