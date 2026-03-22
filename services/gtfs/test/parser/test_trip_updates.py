"""
Unit tests for src/parser/trip_updates.py :: _parse_trip_updates
"""
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_feed(entities):
    """Build a minimal mock FeedMessage with the given entity list."""
    feed = MagicMock()
    feed.entity = entities
    return feed


def _make_entity(entity_id="e1", has_trip_update=True, trip_update=None):
    entity = MagicMock()
    entity.id = entity_id
    entity.HasField = lambda field: field == "trip_update" and has_trip_update
    entity.trip_update = trip_update or MagicMock()
    return entity


def _make_trip(
    trip_id="T1",
    route_id="R1",
    direction_id=0,
    start_time="08:00:00",
    start_date="20240101",
    schedule_relationship=0,
):
    trip = MagicMock()
    trip.trip_id = trip_id
    trip.route_id = route_id
    trip.direction_id = direction_id
    trip.start_time = start_time
    trip.start_date = start_date
    trip.schedule_relationship = schedule_relationship
    return trip


def _make_vehicle(vid="V1", label="Bus 1"):
    vehicle = MagicMock()
    vehicle.id = vid
    vehicle.label = label
    return vehicle


def _make_stop_time_update(
    stop_sequence=1,
    stop_id="S1",
    has_arrival=True,
    has_departure=True,
    schedule_relationship=0,
):
    stu = MagicMock()
    stu.stop_sequence = stop_sequence
    stu.stop_id = stop_id
    stu.schedule_relationship = schedule_relationship

    def stu_has_field(field):
        if field == "arrival":
            return has_arrival
        if field == "departure":
            return has_departure
        return False

    stu.HasField = stu_has_field
    stu.arrival = MagicMock()
    stu.departure = MagicMock()
    return stu


def _make_trip_update(
    trip=None,
    has_vehicle=True,
    vehicle=None,
    stop_time_updates=None,
    timestamp=1700000000,
    delay=30,
):
    tu = MagicMock()
    tu.trip = trip or _make_trip()
    tu.HasField = lambda field: field == "vehicle" and has_vehicle
    tu.vehicle = vehicle or _make_vehicle()
    tu.stop_time_update = stop_time_updates if stop_time_updates is not None else []
    tu.timestamp = timestamp
    tu.delay = delay
    return tu


# ---------------------------------------------------------------------------
# The module under test – patch the _stop_time_event helper so tests remain
# independent of its implementation.
# ---------------------------------------------------------------------------

STOP_TIME_EVENT_PATH = "src.parser.trip_updates._stop_time_event"
MODULE_PATH = "src.parser.trip_updates._parse_trip_updates"


@pytest.fixture(autouse=True)
def mock_stop_time_event():
    """Replace _stop_time_event with a simple identity stub."""
    with patch(STOP_TIME_EVENT_PATH, side_effect=lambda ev: {"mocked": True}) as m:
        yield m


@pytest.fixture()
def parse():
    from src.parser.trip_updates import _parse_trip_updates
    return _parse_trip_updates


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEmptyFeed:
    def test_empty_entity_list_returns_empty_list(self, parse):
        feed = _make_feed([])
        assert parse(feed) == []


class TestEntityFiltering:
    def test_entity_without_trip_update_is_skipped(self, parse):
        entity = _make_entity(has_trip_update=False)
        feed = _make_feed([entity])
        assert parse(feed) == []

    def test_mixed_entities_only_trip_update_entities_returned(self, parse):
        non_tu = _make_entity(entity_id="skip", has_trip_update=False)
        tu_entity = _make_entity(
            entity_id="keep",
            has_trip_update=True,
            trip_update=_make_trip_update(stop_time_updates=[]),
        )
        feed = _make_feed([non_tu, tu_entity])
        result = parse(feed)
        assert len(result) == 1
        assert result[0]["id"] == "keep"


class TestEntityId:
    def test_entity_id_is_preserved(self, parse):
        tu = _make_trip_update(stop_time_updates=[])
        entity = _make_entity(entity_id="my-entity-42", trip_update=tu)
        result = parse(_make_feed([entity]))
        assert result[0]["id"] == "my-entity-42"


class TestTripFields:
    def test_trip_fields_mapped_correctly(self, parse):
        trip = _make_trip(
            trip_id="TRIP99",
            route_id="ROUTE7",
            direction_id=1,
            start_time="09:30:00",
            start_date="20240615",
            schedule_relationship=2,
        )
        tu = _make_trip_update(trip=trip, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]

        assert result["trip"]["trip_id"] == "TRIP99"
        assert result["trip"]["route_id"] == "ROUTE7"
        assert result["trip"]["direction_id"] == 1
        assert result["trip"]["start_time"] == "09:30:00"
        assert result["trip"]["start_date"] == "20240615"
        assert result["trip"]["schedule_relationship"] == 2

    def test_empty_trip_id_becomes_none(self, parse):
        trip = _make_trip(trip_id="")
        tu = _make_trip_update(trip=trip, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["trip"]["trip_id"] is None

    def test_empty_route_id_becomes_none(self, parse):
        trip = _make_trip(route_id="")
        tu = _make_trip_update(trip=trip, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["trip"]["route_id"] is None

    def test_empty_start_time_becomes_none(self, parse):
        trip = _make_trip(start_time="")
        tu = _make_trip_update(trip=trip, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["trip"]["start_time"] is None

    def test_empty_start_date_becomes_none(self, parse):
        trip = _make_trip(start_date="")
        tu = _make_trip_update(trip=trip, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["trip"]["start_date"] is None


class TestVehicleField:
    def test_vehicle_present_when_has_field_true(self, parse):
        vehicle = _make_vehicle(vid="BUS-01", label="Downtown Express")
        tu = _make_trip_update(has_vehicle=True, vehicle=vehicle, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]

        assert result["vehicle"] == {"id": "BUS-01", "label": "Downtown Express"}

    def test_vehicle_is_none_when_has_field_false(self, parse):
        tu = _make_trip_update(has_vehicle=False, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["vehicle"] is None

    def test_vehicle_id_empty_string_becomes_none(self, parse):
        vehicle = _make_vehicle(vid="", label="X")
        tu = _make_trip_update(has_vehicle=True, vehicle=vehicle, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["vehicle"]["id"] is None

    def test_vehicle_label_empty_string_becomes_none(self, parse):
        vehicle = _make_vehicle(vid="V1", label="")
        tu = _make_trip_update(has_vehicle=True, vehicle=vehicle, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["vehicle"]["label"] is None


class TestStopTimeUpdates:
    def test_no_stop_time_updates_returns_empty_list(self, parse):
        tu = _make_trip_update(stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["stop_time_updates"] == []

    def test_stop_time_update_fields_mapped(self, parse):
        stu = _make_stop_time_update(
            stop_sequence=5,
            stop_id="STOP_X",
            has_arrival=True,
            has_departure=True,
            schedule_relationship=1,
        )
        tu = _make_trip_update(stop_time_updates=[stu])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        entry = result["stop_time_updates"][0]

        assert entry["stop_sequence"] == 5
        assert entry["stop_id"] == "STOP_X"
        assert entry["arrival"] == {"mocked": True}
        assert entry["departure"] == {"mocked": True}
        assert entry["schedule_relationship"] == 1

    def test_arrival_none_when_not_present(self, parse):
        stu = _make_stop_time_update(has_arrival=False, has_departure=True)
        tu = _make_trip_update(stop_time_updates=[stu])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["stop_time_updates"][0]["arrival"] is None

    def test_departure_none_when_not_present(self, parse):
        stu = _make_stop_time_update(has_arrival=True, has_departure=False)
        tu = _make_trip_update(stop_time_updates=[stu])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["stop_time_updates"][0]["departure"] is None

    def test_stop_id_empty_string_becomes_none(self, parse):
        stu = _make_stop_time_update(stop_id="")
        tu = _make_trip_update(stop_time_updates=[stu])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["stop_time_updates"][0]["stop_id"] is None

    def test_multiple_stop_time_updates_preserved_in_order(self, parse):
        stus = [_make_stop_time_update(stop_sequence=i, stop_id=f"S{i}") for i in range(3)]
        tu = _make_trip_update(stop_time_updates=stus)
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]

        assert len(result["stop_time_updates"]) == 3
        assert [s["stop_sequence"] for s in result["stop_time_updates"]] == [0, 1, 2]

    def test_stop_time_event_called_for_arrival_and_departure(
        self, parse, mock_stop_time_event
    ):
        stu = _make_stop_time_update(has_arrival=True, has_departure=True)
        tu = _make_trip_update(stop_time_updates=[stu])
        parse(_make_feed([_make_entity(trip_update=tu)]))

        assert mock_stop_time_event.call_count == 2
        mock_stop_time_event.assert_any_call(stu.arrival)
        mock_stop_time_event.assert_any_call(stu.departure)


class TestTimestampAndDelay:
    def test_timestamp_is_preserved(self, parse):
        tu = _make_trip_update(timestamp=1700000123, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["timestamp"] == 1700000123

    def test_zero_timestamp_becomes_none(self, parse):
        tu = _make_trip_update(timestamp=0, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["timestamp"] is None

    def test_delay_is_preserved(self, parse):
        tu = _make_trip_update(delay=120, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["delay"] == 120

    def test_zero_delay_becomes_none(self, parse):
        tu = _make_trip_update(delay=0, stop_time_updates=[])
        result = parse(_make_feed([_make_entity(trip_update=tu)]))[0]
        assert result["delay"] is None


class TestMultipleEntities:
    def test_multiple_trip_update_entities_all_returned(self, parse):
        entities = [
            _make_entity(entity_id=f"e{i}", trip_update=_make_trip_update(stop_time_updates=[]))
            for i in range(4)
        ]
        result = parse(_make_feed(entities))
        assert len(result) == 4
        assert [r["id"] for r in result] == ["e0", "e1", "e2", "e3"]
