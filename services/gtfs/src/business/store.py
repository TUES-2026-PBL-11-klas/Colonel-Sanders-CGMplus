import threading


_lock = threading.Lock()

_store: dict = {
    "alerts":            {"fetched_at": None, "header": {}, "entities": []},
    "trip_updates":      {"fetched_at": None, "header": {}, "entities": []},
    "vehicle_positions": {"fetched_at": None, "header": {}, "entities": []},
    "static": {
        "fetched_at": None,
        "agency":     [],
        "routes":     [],
        "stops":      [],
        "trips":      [],
        "calendar":   [],
    },
}


def _snapshot(key: str) -> dict:
    with _lock:
        import copy
        return copy.deepcopy(_store[key])
