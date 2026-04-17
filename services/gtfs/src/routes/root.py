from flask_smorest import Blueprint
from flask import jsonify
from ..business.store import _store, _lock

blp = Blueprint("root", __name__, description="API root and status endpoints.")


@blp.route("/", methods=["GET"])
def index():
    """API root — lists available endpoints and last fetch times."""
    with _lock:
        status = {
            k: {
                "fetched_at":   v.get("fetched_at"),
                "entity_count": len(v.get("entities", v.get("routes", []))),
            }
            for k, v in _store.items()
        }
    return jsonify({
        "service": "Sofia Transit GTFS API",
        "endpoints": {
            "GET /alerts":                  "Service alerts",
            "GET /trip-updates":            "Real-time trip updates",
            "GET /vehicle-positions":       "Live vehicle positions",
            "GET /vehicle-positions/route/<route_id>": "Filter by route",
            "GET /static/routes":           "All routes",
            "GET /static/stops":            "All stops",
            "GET /static/trips":            "All trips",
            "GET /static/agency":           "Agency info",
            "GET /static/calendar":         "Calendar",
            "GET /status":                  "Feed freshness status",
        },
        "feed_status": status,
    })


@blp.route("/status", methods=["GET"])
def status():
    with _lock:
        return jsonify({
            k: {
                "fetched_at": v.get("fetched_at"),
                "count": len(
                    v.get(
                        "entities",
                        v.get("routes", v.get("stops", []))
                    )
                ),
            }
            for k, v in _store.items()
        })
