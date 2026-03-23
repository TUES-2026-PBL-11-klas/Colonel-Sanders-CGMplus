from flask_smorest import Blueprint
from flask import jsonify, request
from ..business.store import _snapshot

blp = Blueprint(
    "realtime",
    __name__,
    description="Real-time GTFS feed endpoints."
)


@blp.route("/alerts", methods=["GET"])
def alerts():
    data = _snapshot("alerts")
    return jsonify({
        "fetched_at":   data["fetched_at"],
        "header":       data["header"],
        "count":        len(data["entities"]),
        "alerts":       data["entities"],
    })


@blp.route("/trip-updates", methods=["GET"])
def trip_updates():
    data = _snapshot("trip_updates")
    route_id = request.args.get("route_id")
    entities = data["entities"]
    if route_id:
        entities = [
            e for e in entities
            if e.get("trip", {}) and e["trip"].get("route_id") == route_id
        ]
    return jsonify({
        "fetched_at":    data["fetched_at"],
        "header":        data["header"],
        "count":         len(entities),
        "trip_updates":  entities,
    })


@blp.route("/vehicle-positions", methods=["GET"])
def vehicle_positions():
    data = _snapshot("vehicle_positions")
    route_id = request.args.get("route_id")
    entities = data["entities"]
    if route_id:
        entities = [
            e for e in entities
            if e.get("trip") and e["trip"].get("route_id") == route_id
        ]
    return jsonify({
        "fetched_at":        data["fetched_at"],
        "header":            data["header"],
        "count":             len(entities),
        "vehicle_positions": entities,
    })


@blp.route("/vehicle-positions/route/<string:route_id>", methods=["GET"])
def vehicle_positions_by_route(route_id: str):
    data = _snapshot("vehicle_positions")
    entities = [
        e for e in data["entities"]
        if e.get("trip") and e["trip"].get("route_id") == route_id
    ]
    return jsonify({
        "fetched_at":        data["fetched_at"],
        "route_id":          route_id,
        "count":             len(entities),
        "vehicle_positions": entities,
    })
