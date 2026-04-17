from unittest.mock import patch
from google.transit import gtfs_realtime_pb2

from src.parser.alerts import _parse_alerts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_translation(text: str, language: str = "en") -> gtfs_realtime_pb2.TranslatedString:
    ts = gtfs_realtime_pb2.TranslatedString()
    t = ts.translation.add()
    t.text = text
    t.language = language
    return ts


def _make_feed(*entities: gtfs_realtime_pb2.FeedEntity) -> gtfs_realtime_pb2.FeedMessage:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    for entity in entities:
        e = feed.entity.add()
        e.CopyFrom(entity)
    return feed


def _make_alert_entity(
    entity_id: str = "alert-1",
    active_periods=None,
    informed_entities=None,
    cause: int = gtfs_realtime_pb2.Alert.UNKNOWN_CAUSE,
    effect: int = gtfs_realtime_pb2.Alert.UNKNOWN_EFFECT,
    url: str = "",
    header: str = "",
    description: str = "",
) -> gtfs_realtime_pb2.FeedEntity:
    entity = gtfs_realtime_pb2.FeedEntity()
    entity.id = entity_id

    alert = entity.alert

    for start, end in (active_periods or []):
        p = alert.active_period.add()
        p.start = start
        p.end = end

    for ie_kwargs in (informed_entities or []):
        ie = alert.informed_entity.add()
        if ie_kwargs.get("agency_id"):
            ie.agency_id = ie_kwargs["agency_id"]
        if ie_kwargs.get("route_id"):
            ie.route_id = ie_kwargs["route_id"]
        if ie_kwargs.get("route_type"):
            ie.route_type = ie_kwargs["route_type"]
        if ie_kwargs.get("stop_id"):
            ie.stop_id = ie_kwargs["stop_id"]
        if ie_kwargs.get("trip"):
            trip_data = ie_kwargs["trip"]
            if trip_data.get("trip_id"):
                ie.trip.trip_id = trip_data["trip_id"]
            if trip_data.get("route_id"):
                ie.trip.route_id = trip_data["route_id"]
            if "direction_id" in trip_data:
                ie.trip.direction_id = trip_data["direction_id"]

    alert.cause = cause
    alert.effect = effect

    if url:
        alert.url.CopyFrom(_make_translation(url))
    if header:
        alert.header_text.CopyFrom(_make_translation(header))
    if description:
        alert.description_text.CopyFrom(_make_translation(description))

    return entity


# ---------------------------------------------------------------------------
# Patch target for _translated
# ---------------------------------------------------------------------------

TRANSLATED_PATH = "src.parser.alerts._translated"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestParseAlertsEmptyFeed:
    def test_empty_feed_returns_empty_list(self):
        feed = _make_feed()
        assert _parse_alerts(feed) == []

    def test_entity_without_alert_field_is_skipped(self):
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.header.gtfs_realtime_version = "2.0"
        # Add a vehicle_position entity (not an alert)
        e = feed.entity.add()
        e.id = "vp-1"
        e.vehicle.vehicle.id = "bus-42"
        assert _parse_alerts(feed) == []


class TestParseAlertsBasicFields:
    def test_entity_id_is_preserved(self):
        entity = _make_alert_entity(entity_id="my-alert-id")
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["id"] == "my-alert-id"

    def test_cause_and_effect_are_passed_through(self):
        entity = _make_alert_entity(
            cause=gtfs_realtime_pb2.Alert.STRIKE,
            effect=gtfs_realtime_pb2.Alert.DETOUR,
        )
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["cause"] == gtfs_realtime_pb2.Alert.STRIKE
        assert result[0]["effect"] == gtfs_realtime_pb2.Alert.DETOUR

    def test_translated_fields_delegate_to_helper(self):
        entity = _make_alert_entity(url="http://example.com", header="Disruption", description="Details")
        feed = _make_feed(entity)

        return_values = iter(["http://example.com", "Disruption", "Details"])
        with patch(TRANSLATED_PATH, side_effect=lambda _: next(return_values)) as mock_translated:
            result = _parse_alerts(feed)

        assert mock_translated.call_count == 3
        assert result[0]["url"] == "http://example.com"
        assert result[0]["header_text"] == "Disruption"
        assert result[0]["description"] == "Details"

    def test_translated_fields_return_none_when_empty(self):
        entity = _make_alert_entity()
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["url"] is None
        assert result[0]["header_text"] is None
        assert result[0]["description"] is None


class TestParseAlertsActivePeriods:
    def test_no_active_periods(self):
        entity = _make_alert_entity(active_periods=[])
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["active_periods"] == []

    def test_single_active_period(self):
        entity = _make_alert_entity(active_periods=[(1000, 2000)])
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["active_periods"] == [{"start": 1000, "end": 2000}]

    def test_multiple_active_periods(self):
        entity = _make_alert_entity(active_periods=[(1000, 2000), (3000, 4000)])
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["active_periods"] == [
            {"start": 1000, "end": 2000},
            {"start": 3000, "end": 4000},
        ]


class TestParseAlertsInformedEntities:
    def test_no_informed_entities(self):
        entity = _make_alert_entity(informed_entities=[])
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["informed_entities"] == []

    def test_informed_entity_with_agency_and_route(self):
        entity = _make_alert_entity(
            informed_entities=[{"agency_id": "agency-1", "route_id": "route-42"}]
        )
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        ie = result[0]["informed_entities"][0]
        assert ie["agency_id"] == "agency-1"
        assert ie["route_id"] == "route-42"
        assert ie["trip"] is None

    def test_informed_entity_empty_strings_become_none(self):
        entity = _make_alert_entity(informed_entities=[{}])
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        ie = result[0]["informed_entities"][0]
        assert ie["agency_id"] is None
        assert ie["route_id"] is None
        assert ie["stop_id"] is None

    def test_informed_entity_route_type_zero_becomes_none(self):
        # route_type == 0 is falsy — the parser maps it to None
        entity = _make_alert_entity(informed_entities=[{"route_type": 0}])
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["informed_entities"][0]["route_type"] is None

    def test_informed_entity_non_zero_route_type(self):
        entity = _make_alert_entity(informed_entities=[{"route_type": 3}])
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert result[0]["informed_entities"][0]["route_type"] == 3

    def test_informed_entity_with_trip(self):
        entity = _make_alert_entity(
            informed_entities=[
                {"trip": {"trip_id": "trip-1", "route_id": "route-7", "direction_id": 1}}
            ]
        )
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        trip = result[0]["informed_entities"][0]["trip"]
        assert trip is not None
        assert trip["trip_id"] == "trip-1"
        assert trip["route_id"] == "route-7"
        assert trip["direction_id"] == 1

    def test_informed_entity_trip_empty_strings_become_none(self):
        entity = _make_alert_entity(
            informed_entities=[{"trip": {"direction_id": 0}}]
        )
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        trip = result[0]["informed_entities"][0]["trip"]
        assert trip["trip_id"] is None
        assert trip["route_id"] is None

    def test_multiple_informed_entities(self):
        entity = _make_alert_entity(
            informed_entities=[
                {"agency_id": "agency-1"},
                {"route_id": "route-2"},
                {"stop_id": "stop-3"},
            ]
        )
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        ies = result[0]["informed_entities"]
        assert len(ies) == 3
        assert ies[0]["agency_id"] == "agency-1"
        assert ies[1]["route_id"] == "route-2"
        assert ies[2]["stop_id"] == "stop-3"


class TestParseAlertsMultipleEntities:
    def test_multiple_alerts_all_returned(self):
        entities = [
            _make_alert_entity(entity_id="a1"),
            _make_alert_entity(entity_id="a2"),
            _make_alert_entity(entity_id="a3"),
        ]
        feed = _make_feed(*entities)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert len(result) == 3
        assert [r["id"] for r in result] == ["a1", "a2", "a3"]

    def test_mixed_entity_types_only_alerts_returned(self):
        alert_entity = _make_alert_entity(entity_id="alert-only")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.header.gtfs_realtime_version = "2.0"

        # non-alert entity
        vp = feed.entity.add()
        vp.id = "vp-1"
        vp.vehicle.vehicle.id = "bus-1"

        alert_copy = feed.entity.add()
        alert_copy.CopyFrom(alert_entity)

        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)

        assert len(result) == 1
        assert result[0]["id"] == "alert-only"


class TestParseAlertsOutputSchema:
    """Ensure every returned dict has exactly the expected top-level keys."""

    EXPECTED_KEYS = {"id", "active_periods", "informed_entities", "cause", "effect", "url", "header_text", "description"}

    def test_output_dict_has_all_required_keys(self):
        entity = _make_alert_entity()
        feed = _make_feed(entity)
        with patch(TRANSLATED_PATH, return_value=None):
            result = _parse_alerts(feed)
        assert set(result[0].keys()) == self.EXPECTED_KEYS
