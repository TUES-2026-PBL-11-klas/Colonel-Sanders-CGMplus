from google.transit import gtfs_realtime_pb2
from ..util.time import _stop_time_event


def _parse_trip_updates(feed: gtfs_realtime_pb2.FeedMessage) -> list:
    out = []
    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue
        tu = entity.trip_update
        out.append({
            "id": entity.id,
            "trip": {
                "trip_id":    tu.trip.trip_id or None,
                "route_id":   tu.trip.route_id or None,
                "direction_id": tu.trip.direction_id,
                "start_time": tu.trip.start_time or None,
                "start_date": tu.trip.start_date or None,
                "schedule_relationship": tu.trip.schedule_relationship,
            },
            "vehicle": {
                "id":    tu.vehicle.id or None,
                "label": tu.vehicle.label or None,
            } if tu.HasField("vehicle") else None,
            "stop_time_updates": [
                {
                    "stop_sequence": stu.stop_sequence,
                    "stop_id":       stu.stop_id or None,
                    "arrival": (
                        _stop_time_event(stu.arrival)
                        if stu.HasField("arrival")
                        else None
                    ),
                    "departure": (
                        _stop_time_event(stu.departure)
                        if stu.HasField("departure")
                        else None
                    ),
                    "schedule_relationship": stu.schedule_relationship,
                }
                for stu in tu.stop_time_update
            ],
            "timestamp": tu.timestamp or None,
            "delay":     tu.delay or None,
        })
    return out
