from google.transit import gtfs_realtime_pb2
from ..util.gtfs import _translated


def _parse_alerts(feed: gtfs_realtime_pb2.FeedMessage) -> list:
    out = []
    for entity in feed.entity:
        if not entity.HasField("alert"):
            continue
        a = entity.alert
        out.append({
            "id": entity.id,
            "active_periods": [
                {"start": p.start, "end": p.end}
                for p in a.active_period
            ],
            "informed_entities": [
                {
                    "agency_id":   ie.agency_id or None,
                    "route_id":    ie.route_id or None,
                    "route_type":  ie.route_type if ie.route_type else None,
                    "trip":        {
                        "trip_id":    ie.trip.trip_id or None,
                        "route_id":   ie.trip.route_id or None,
                        "direction_id": ie.trip.direction_id,
                    } if ie.HasField("trip") else None,
                    "stop_id":     ie.stop_id or None,
                }
                for ie in a.informed_entity
            ],
            "cause":   a.cause,
            "effect":  a.effect,
            "url":          _translated(a.url),
            "header_text":  _translated(a.header_text),
            "description":  _translated(a.description_text),
        })
    return out
