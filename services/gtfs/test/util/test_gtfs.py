from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.util.gtfs import _translated, _header_to_dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_translation(language: str, text: str) -> MagicMock:
    t = MagicMock()
    t.language = language
    t.text = text
    return t


def make_translated_string(translations: list) -> MagicMock:
    field = MagicMock()
    field.translation = translations
    return field


def make_header(
    gtfs_realtime_version: str = "2.0",
    incrementality: int = 0,
    timestamp: int | None = 1_700_000_000,
) -> MagicMock:
    h = MagicMock()
    h.gtfs_realtime_version = gtfs_realtime_version
    h.incrementality = incrementality
    h.timestamp = timestamp
    return h


# ---------------------------------------------------------------------------
# _translated
# ---------------------------------------------------------------------------

class TestTranslated:
    def test_single_translation(self):
        field = make_translated_string([make_translation("en", "Hello")])
        result = _translated(field)
        assert result == [{"language": "en", "text": "Hello"}]

    def test_multiple_translations(self):
        field = make_translated_string([
            make_translation("en", "Hello"),
            make_translation("de", "Hallo"),
            make_translation("fr", "Bonjour"),
        ])
        result = _translated(field)
        assert result == [
            {"language": "en", "text": "Hello"},
            {"language": "de", "text": "Hallo"},
            {"language": "fr", "text": "Bonjour"},
        ]

    def test_empty_translations(self):
        field = make_translated_string([])
        result = _translated(field)
        assert result == []

    def test_returns_list(self):
        field = make_translated_string([make_translation("en", "Test")])
        assert isinstance(_translated(field), list)

    def test_each_item_has_language_and_text_keys(self):
        field = make_translated_string([make_translation("es", "Hola")])
        item = _translated(field)[0]
        assert "language" in item
        assert "text" in item

    def test_empty_language_and_text(self):
        field = make_translated_string([make_translation("", "")])
        assert _translated(field) == [{"language": "", "text": ""}]

    def test_preserves_order(self):
        langs = ["en", "de", "fr", "ja", "zh"]
        field = make_translated_string(
            [make_translation(lang, lang.upper()) for lang in langs]
        )
        result = _translated(field)
        assert [item["language"] for item in result] == langs


# ---------------------------------------------------------------------------
# _header_to_dict
# ---------------------------------------------------------------------------

class TestHeaderToDict:
    def test_basic_structure(self):
        header = make_header()
        result = _header_to_dict(header)
        assert set(result.keys()) == {
            "gtfs_realtime_version",
            "incrementality",
            "timestamp",
            "timestamp_iso",
        }

    def test_values_passed_through(self):
        header = make_header(
            gtfs_realtime_version="2.0",
            incrementality=0,
            timestamp=1_700_000_000,
        )
        result = _header_to_dict(header)
        assert result["gtfs_realtime_version"] == "2.0"
        assert result["incrementality"] == 0
        assert result["timestamp"] == 1_700_000_000

    def test_timestamp_iso_is_utc(self):
        ts = 1_700_000_000
        header = make_header(timestamp=ts)
        result = _header_to_dict(header)
        expected = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        assert result["timestamp_iso"] == expected

    def test_timestamp_iso_ends_with_utc_offset(self):
        header = make_header(timestamp=1_700_000_000)
        iso = _header_to_dict(header)["timestamp_iso"]
        # datetime.isoformat() with UTC tz appends '+00:00'
        assert iso.endswith("+00:00")

    def test_timestamp_zero_produces_iso(self):
        """timestamp=0 is falsy in Python — should yield None."""
        header = make_header(timestamp=0)
        result = _header_to_dict(header)
        assert result["timestamp_iso"] is None

    def test_timestamp_none_yields_none_iso(self):
        header = make_header(timestamp=None)
        result = _header_to_dict(header)
        assert result["timestamp"] is None
        assert result["timestamp_iso"] is None

    def test_known_timestamp_iso_value(self):
        # 2023-11-14 22:13:20 UTC
        header = make_header(timestamp=1_700_000_000)
        result = _header_to_dict(header)
        assert result["timestamp_iso"] == "2023-11-14T22:13:20+00:00"

    def test_incrementality_non_zero(self):
        header = make_header(incrementality=1)
        result = _header_to_dict(header)
        assert result["incrementality"] == 1

    def test_different_gtfs_version(self):
        header = make_header(gtfs_realtime_version="1.0")
        result = _header_to_dict(header)
        assert result["gtfs_realtime_version"] == "1.0"

    def test_returns_dict(self):
        assert isinstance(_header_to_dict(make_header()), dict)
