from flask_smorest import Blueprint
from flask import jsonify, request
from ..business.store import _snapshot

blp = Blueprint("static", __name__, description="Static GTFS feed endpoints.")


def _paginate(items: list, page: int, per_page: int) -> dict:
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    (total + per_page - 1) // per_page,
        "items":    items[start:end],
    }


def _static_endpoint(key: str, item_key: str, search_field: str | None = None):
    data = _snapshot("static")
    items = data.get(key, [])
    q = request.args.get("q", "").strip().lower()
    if q and search_field:
        items = [i for i in items if q in i.get(search_field, "").lower()]
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(500, max(1, int(request.args.get("per_page", 100))))
    paged = _paginate(items, page, per_page)
    return jsonify({
        "fetched_at": data["fetched_at"],
        item_key:     paged["items"],
        "pagination": {k: v for k, v in paged.items() if k != "items"},
    })


@blp.route("/static/routes", methods=["GET"])
def static_routes():
    return _static_endpoint("routes", "routes", "route_short_name")


@blp.route("/static/routes/<string:route_id>", methods=["GET"])
def static_route(route_id: str):
    data = _snapshot("static")
    found = [r for r in data["routes"] if r.get("route_id") == route_id]
    if not found:
        return jsonify({"error": "Route not found"}), 404
    return jsonify({"fetched_at": data["fetched_at"], "route": found[0]})


@blp.route("/static/stops", methods=["GET"])
def static_stops():
    return _static_endpoint("stops", "stops", "stop_name")


@blp.route("/static/stops/<string:stop_id>", methods=["GET"])
def static_stop(stop_id: str):
    data = _snapshot("static")
    found = [s for s in data["stops"] if s.get("stop_id") == stop_id]
    if not found:
        return jsonify({"error": "Stop not found"}), 404
    return jsonify({"fetched_at": data["fetched_at"], "stop": found[0]})


@blp.route("/static/trips", methods=["GET"])
def static_trips():
    route_id = request.args.get("route_id")
    data = _snapshot("static")
    items = data.get("trips", [])
    if route_id:
        items = [t for t in items if t.get("route_id") == route_id]
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(500, max(1, int(request.args.get("per_page", 100))))
    paged = _paginate(items, page, per_page)
    return jsonify({
        "fetched_at": data["fetched_at"],
        "trips":      paged["items"],
        "pagination": {k: v for k, v in paged.items() if k != "items"},
    })


@blp.route("/static/agency", methods=["GET"])
def static_agency():
    data = _snapshot("static")
    return jsonify({
        "fetched_at": data["fetched_at"],
        "agency": data["agency"]
    })


@blp.route("/static/calendar", methods=["GET"])
def static_calendar():
    data = _snapshot("static")
    return jsonify({
        "fetched_at": data["fetched_at"],
        "calendar": data["calendar"]
    })
