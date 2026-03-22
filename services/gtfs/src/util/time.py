from datetime import datetime, timezone


def _stop_time_event(ste) -> dict:
    return {
        "delay": ste.delay if ste.delay else None,
        "time": ste.time if ste.time else None,
        "time_iso": (
            datetime.fromtimestamp(
                ste.time,
                tz=timezone.utc
            ).isoformat()
            if ste.time
            else None
        ),
        "uncertainty": ste.uncertainty if ste.uncertainty else None,
    }
