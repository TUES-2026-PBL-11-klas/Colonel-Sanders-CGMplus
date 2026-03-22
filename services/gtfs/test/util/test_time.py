from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.util.time import _stop_time_event


def make_ste(delay=None, time=None, uncertainty=None):
    ste = MagicMock()
    ste.delay = delay
    ste.time = time
    ste.uncertainty = uncertainty
    return ste


class TestStopTimeEvent:
    def test_all_fields_present(self):
        ste = make_ste(delay=30, time=1700000000, uncertainty=60)
        result = _stop_time_event(ste)

        assert result["delay"] == 30
        assert result["time"] == 1700000000
        assert result["time_iso"] == "2023-11-14T22:13:20+00:00"
        assert result["uncertainty"] == 60

    def test_all_fields_none(self):
        ste = make_ste()
        result = _stop_time_event(ste)

        assert result["delay"] is None
        assert result["time"] is None
        assert result["time_iso"] is None
        assert result["uncertainty"] is None

    def test_time_iso_is_utc(self):
        ste = make_ste(time=0)
        result = _stop_time_event(ste)

        assert result["time_iso"] == "1970-01-01T00:00:00+00:00"

    def test_time_iso_matches_timestamp(self):
        timestamp = 1609459200  # 2021-01-01T00:00:00Z
        ste = make_ste(time=timestamp)
        result = _stop_time_event(ste)

        expected = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        assert result["time_iso"] == expected

    def test_delay_zero_treated_as_falsy(self):
        ste = make_ste(delay=0)
        result = _stop_time_event(ste)

        assert result["delay"] is None

    def test_uncertainty_zero_treated_as_falsy(self):
        ste = make_ste(uncertainty=0)
        result = _stop_time_event(ste)

        assert result["uncertainty"] is None

    def test_returns_dict_with_expected_keys(self):
        ste = make_ste()
        result = _stop_time_event(ste)

        assert set(result.keys()) == {"delay", "time", "time_iso", "uncertainty"}

    def test_negative_delay(self):
        ste = make_ste(delay=-10)
        result = _stop_time_event(ste)

        assert result["delay"] == -10

    def test_large_timestamp(self):
        timestamp = 32503680000  # 3000-01-01T00:00:00Z
        ste = make_ste(time=timestamp)
        result = _stop_time_event(ste)

        assert result["time"] == timestamp
        assert result["time_iso"] is not None
        expected = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        assert result["time_iso"] == expected
