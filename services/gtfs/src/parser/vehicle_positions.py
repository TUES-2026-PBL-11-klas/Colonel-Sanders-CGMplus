from google.transit import gtfs_realtime_pb2


def _parse_vehicle_positions(feed: gtfs_realtime_pb2.FeedMessage) -> list:
    out = []
    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue
        v = entity.vehicle
        out.append({
            "id": entity.id,
            "trip": {
                "trip_id":    v.trip.trip_id or None,
                "route_id":   v.trip.route_id or None,
                "direction_id": v.trip.direction_id,
                "start_time": v.trip.start_time or None,
                "start_date": v.trip.start_date or None,
            } if v.HasField("trip") else None,
            "vehicle": {
                "id":           v.vehicle.id or None,
                "label":        v.vehicle.label or None,
                "license_plate": v.vehicle.license_plate or None,
            } if v.HasField("vehicle") else None,
            "position": {
                "latitude":  v.position.latitude,
                "longitude": v.position.longitude,
                "bearing":   v.position.bearing,
                "speed":     v.position.speed,
            } if v.HasField("position") else None,
            "current_stop_sequence": v.current_stop_sequence or None,
            "stop_id":      v.stop_id or None,
            "current_status": v.current_status,
            "timestamp":    v.timestamp or None,
            "congestion_level": v.congestion_level,
            "occupancy_status": v.occupancy_status,
        })
    return out
