from datetime import datetime, timezone


def _translated(field) -> list:
    """Return list of {language, text} from a TranslatedString."""
    return [
        {"language": t.language, "text": t.text}
        for t in field.translation
    ]


def _header_to_dict(header) -> dict:
    return {
        "gtfs_realtime_version": header.gtfs_realtime_version,
        "incrementality": header.incrementality,
        "timestamp": header.timestamp,
        "timestamp_iso": (
            datetime.fromtimestamp(
                header.timestamp,
                tz=timezone.utc
            ).isoformat()
            if header.timestamp
            else None
        ),
    }
