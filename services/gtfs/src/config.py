FEEDS = {
    "alerts": "https://gtfs.sofiatraffic.bg/api/v1/alerts",
    "trip_updates": "https://gtfs.sofiatraffic.bg/api/v1/trip-updates",
    "vehicle_positions": (
        "https://gtfs.sofiatraffic.bg/api/v1/vehicle-positions"
    ),
}

STATIC_URL = "https://gtfs.sofiatraffic.bg/api/v1/static"

RT_INTERVAL = 15
STATIC_INTERVAL = 3600
REQUEST_TIMEOUT = 20
