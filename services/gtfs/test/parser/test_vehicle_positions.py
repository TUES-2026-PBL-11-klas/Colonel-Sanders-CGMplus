import pytest
from google.transit import gtfs_realtime_pb2

# ---------------------------------------------------------------------------
# Import the function under test
# ---------------------------------------------------------------------------
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "parser"))
from src.parser.vehicle_positions import _parse_vehicle_positions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_feed(*entities: gtfs_realtime_pb2.FeedEntity) -> gtfs_realtime_pb2.FeedMessage:
    """Wrap one or more FeedEntity objects into a FeedMessage."""
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    for e in entities:
        feed.entity.append(e)
    return feed


def _vehicle_entity(
    entity_id="v1",
    trip_id="T1", route_id="R1", direction_id=0,
    start_time="08:00:00", start_date="20240101",
    vehicle_id="VH1", label="Bus 1", license_plate="ABC123",
    latitude=42.0, longitude=23.0, bearing=180.0, speed=15.0,
    current_stop_sequence=5, stop_id="S10",
    current_status=gtfs_realtime_pb2.VehiclePosition.IN_TRANSIT_TO,
    timestamp=1700000000,
    congestion_level=gtfs_realtime_pb2.VehiclePosition.UNKNOWN_CONGESTION_LEVEL,
    occupancy_status=gtfs_realtime_pb2.VehiclePosition.EMPTY,
) -> gtfs_realtime_pb2.FeedEntity:
    """Build a fully-populated FeedEntity containing a VehiclePosition."""
    e = gtfs_realtime_pb2.FeedEntity()
    e.id = entity_id

    v = e.vehicle
    v.trip.trip_id = trip_id
    v.trip.route_id = route_id
    v.trip.direction_id = direction_id
    v.trip.start_time = start_time
    v.trip.start_date = start_date

    v.vehicle.id = vehicle_id
    v.vehicle.label = label
    v.vehicle.license_plate = license_plate

    v.position.latitude = latitude
    v.position.longitude = longitude
    v.position.bearing = bearing
    v.position.speed = speed

    v.current_stop_sequence = current_stop_sequence
    v.stop_id = stop_id
    v.current_status = current_status
    v.timestamp = timestamp
    v.congestion_level = congestion_level
    v.occupancy_status = occupancy_status

    return e


def _non_vehicle_entity(entity_id="a1") -> gtfs_realtime_pb2.FeedEntity:
    """Build a FeedEntity that contains an Alert (not a vehicle)."""
    e = gtfs_realtime_pb2.FeedEntity()
    e.id = entity_id
    e.alert.cause = gtfs_realtime_pb2.Alert.OTHER_CAUSE
    return e


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestParseVehiclePositionsEmptyAndFiltering:

    def test_empty_feed_returns_empty_list(self):
        feed = _make_feed()
        assert _parse_vehicle_positions(feed) == []

    def test_non_vehicle_entities_are_skipped(self):
        feed = _make_feed(_non_vehicle_entity())
        assert _parse_vehicle_positions(feed) == []

    def test_mixed_entities_only_vehicles_returned(self):
        feed = _make_feed(_non_vehicle_entity("a1"), _vehicle_entity("v1"))
        result = _parse_vehicle_positions(feed)
        assert len(result) == 1
        assert result[0]["id"] == "v1"

    def test_multiple_vehicle_entities_all_returned(self):
        feed = _make_feed(_vehicle_entity("v1"), _vehicle_entity("v2"))
        result = _parse_vehicle_positions(feed)
        assert len(result) == 2
        ids = {r["id"] for r in result}
        assert ids == {"v1", "v2"}


class TestParseVehiclePositionsFullyPopulated:

    def setup_method(self):
        feed = _make_feed(_vehicle_entity())
        self.result = _parse_vehicle_positions(feed)[0]

    def test_entity_id(self):
        assert self.result["id"] == "v1"

    # --- trip sub-dict ---
    def test_trip_trip_id(self):
        assert self.result["trip"]["trip_id"] == "T1"

    def test_trip_route_id(self):
        assert self.result["trip"]["route_id"] == "R1"

    def test_trip_direction_id(self):
        assert self.result["trip"]["direction_id"] == 0

    def test_trip_start_time(self):
        assert self.result["trip"]["start_time"] == "08:00:00"

    def test_trip_start_date(self):
        assert self.result["trip"]["start_date"] == "20240101"

    # --- vehicle sub-dict ---
    def test_vehicle_id(self):
        assert self.result["vehicle"]["id"] == "VH1"

    def test_vehicle_label(self):
        assert self.result["vehicle"]["label"] == "Bus 1"

    def test_vehicle_license_plate(self):
        assert self.result["vehicle"]["license_plate"] == "ABC123"

    # --- position sub-dict ---
    def test_position_latitude(self):
        assert self.result["position"]["latitude"] == pytest.approx(42.0)

    def test_position_longitude(self):
        assert self.result["position"]["longitude"] == pytest.approx(23.0)

    def test_position_bearing(self):
        assert self.result["position"]["bearing"] == pytest.approx(180.0)

    def test_position_speed(self):
        assert self.result["position"]["speed"] == pytest.approx(15.0)

    # --- top-level fields ---
    def test_current_stop_sequence(self):
        assert self.result["current_stop_sequence"] == 5

    def test_stop_id(self):
        assert self.result["stop_id"] == "S10"

    def test_current_status(self):
        assert self.result["current_status"] == gtfs_realtime_pb2.VehiclePosition.IN_TRANSIT_TO

    def test_timestamp(self):
        assert self.result["timestamp"] == 1700000000

    def test_congestion_level(self):
        assert self.result["congestion_level"] == gtfs_realtime_pb2.VehiclePosition.UNKNOWN_CONGESTION_LEVEL

    def test_occupancy_status(self):
        assert self.result["occupancy_status"] == gtfs_realtime_pb2.VehiclePosition.EMPTY


class TestParseVehiclePositionsNoneCoercion:
    """Empty-string / zero falsy values should be coerced to None where applicable."""

    def test_empty_trip_id_becomes_none(self):
        e = _vehicle_entity(trip_id="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["trip"]["trip_id"] is None

    def test_empty_route_id_becomes_none(self):
        e = _vehicle_entity(route_id="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["trip"]["route_id"] is None

    def test_empty_start_time_becomes_none(self):
        e = _vehicle_entity(start_time="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["trip"]["start_time"] is None

    def test_empty_start_date_becomes_none(self):
        e = _vehicle_entity(start_date="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["trip"]["start_date"] is None

    def test_empty_vehicle_id_becomes_none(self):
        e = _vehicle_entity(vehicle_id="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["vehicle"]["id"] is None

    def test_empty_label_becomes_none(self):
        e = _vehicle_entity(label="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["vehicle"]["label"] is None

    def test_empty_license_plate_becomes_none(self):
        e = _vehicle_entity(license_plate="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["vehicle"]["license_plate"] is None

    def test_zero_current_stop_sequence_becomes_none(self):
        e = _vehicle_entity(current_stop_sequence=0)
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["current_stop_sequence"] is None

    def test_empty_stop_id_becomes_none(self):
        e = _vehicle_entity(stop_id="")
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["stop_id"] is None

    def test_zero_timestamp_becomes_none(self):
        e = _vehicle_entity(timestamp=0)
        result = _parse_vehicle_positions(_make_feed(e))[0]
        assert result["timestamp"] is None


class TestParseVehiclePositionsOptionalSubMessages:
    """trip / vehicle / position sub-dicts must be None when the sub-message
    is absent from the protobuf (HasField returns False)."""

    def _entity_without_optional_fields(self) -> gtfs_realtime_pb2.FeedEntity:
        """An entity whose vehicle has no trip, vehicle, or position set."""
        e = gtfs_realtime_pb2.FeedEntity()
        e.id = "bare"
        # Touch the vehicle field so HasField("vehicle") is True on the entity.
        e.vehicle.current_status = gtfs_realtime_pb2.VehiclePosition.IN_TRANSIT_TO
        # Deliberately do NOT set trip / vehicle / position sub-messages.
        return e

    def test_trip_is_none_when_not_set(self):
        result = _parse_vehicle_positions(_make_feed(self._entity_without_optional_fields()))[0]
        assert result["trip"] is None

    def test_vehicle_is_none_when_not_set(self):
        result = _parse_vehicle_positions(_make_feed(self._entity_without_optional_fields()))[0]
        assert result["vehicle"] is None

    def test_position_is_none_when_not_set(self):
        result = _parse_vehicle_positions(_make_feed(self._entity_without_optional_fields()))[0]
        assert result["position"] is None


class TestParseVehiclePositionsOutputStructure:

    def test_output_is_list(self):
        feed = _make_feed(_vehicle_entity())
        assert isinstance(_parse_vehicle_positions(feed), list)

    def test_each_item_has_required_top_level_keys(self):
        required = {
            "id", "trip", "vehicle", "position",
            "current_stop_sequence", "stop_id", "current_status",
            "timestamp", "congestion_level", "occupancy_status",
        }
        feed = _make_feed(_vehicle_entity())
        result = _parse_vehicle_positions(feed)[0]
        assert required.issubset(result.keys())

    def test_trip_sub_dict_has_required_keys(self):
        feed = _make_feed(_vehicle_entity())
        trip = _parse_vehicle_positions(feed)[0]["trip"]
        assert set(trip.keys()) == {"trip_id", "route_id", "direction_id", "start_time", "start_date"}

    def test_vehicle_sub_dict_has_required_keys(self):
        feed = _make_feed(_vehicle_entity())
        vehicle = _parse_vehicle_positions(feed)[0]["vehicle"]
        assert set(vehicle.keys()) == {"id", "label", "license_plate"}

    def test_position_sub_dict_has_required_keys(self):
        feed = _make_feed(_vehicle_entity())
        pos = _parse_vehicle_positions(feed)[0]["position"]
        assert set(pos.keys()) == {"latitude", "longitude", "bearing", "speed"}
