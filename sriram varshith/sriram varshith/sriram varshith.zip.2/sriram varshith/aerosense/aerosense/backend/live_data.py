"""Live weather and air-quality estimates from configured providers."""
import json
import logging
import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from database import fetch_latest_observations, fetch_stations
from ai_service import calculate_cpcb_aqi

_CACHE_SECONDS = 600
_OPENWEATHER_CACHE_SECONDS = 5400
_LOGGER = logging.getLogger(__name__)
_cache_lock = threading.Lock()
_cached_at = 0.0
_cached_observations = []


class LiveDataUnavailable(Exception):
    """Raised when Open-Meteo cannot provide current data and no cache exists."""


def _request_json(base_url, params, provider="Open-Meteo"):
    url = f"{base_url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "AeroSense/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read())
    except HTTPError as error:
        raise LiveDataUnavailable(f"{provider} returned HTTP {error.code}") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise LiveDataUnavailable(f"{provider} request failed") from error


def _as_location_list(data, expected_count):
    locations = data if isinstance(data, list) else [data]
    if len(locations) != expected_count:
        raise LiveDataUnavailable(
            f"Open-Meteo returned {len(locations)} locations; expected {expected_count}"
        )
    return locations


def _observed_at(value):
    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    return timestamp.isoformat()


def _observed_at_unix(value):
    timestamp = _number(value)
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat() if timestamp is not None else None


def _number(value):
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else None


def _timestamp_key(observation):
    value = observation.get("observedAt", "")
    try:
        timestamp = datetime.fromisoformat(value)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc).timestamp()
    except (TypeError, ValueError):
        return 0


def _fetch_openmeteo_current(stations):
    latitudes = ",".join(str(station["latitude"]) for station in stations)
    longitudes = ",".join(str(station["longitude"]) for station in stations)
    shared = {
        "latitude": latitudes,
        "longitude": longitudes,
        "timezone": "Asia/Kolkata",
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        weather_request = executor.submit(
            _request_json,
            "https://api.open-meteo.com/v1/forecast",
            {
                **shared,
                "current": (
                    "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,"
                    "wind_direction_10m,dew_point_2m,weather_code,surface_pressure,"
                    "visibility,precipitation,uv_index"
                ),
                "daily": "sunrise,sunset",
            },
        )
        air_request = executor.submit(
            _request_json,
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            {
                **shared,
                "current": (
                    "pm2_5,pm10,nitrogen_dioxide,sulphur_dioxide,ozone,"
                    "carbon_monoxide,us_aqi,european_aqi"
                ),
            },
        )
        weather_data = _as_location_list(weather_request.result(), len(stations))
        air_data = _as_location_list(air_request.result(), len(stations))

    observations = []
    for station, weather, air in zip(stations, weather_data, air_data):
        weather_current = weather.get("current") or {}
        air_current = air.get("current") or {}
        air_time = air_current.get("time")
        weather_time = weather_current.get("time")

        pm25 = _number(air_current.get("pm2_5"))
        us_aqi = _number(air_current.get("us_aqi"))
        if air_time and (pm25 is not None or us_aqi is not None):
            observation = {
                "source": "aq_station",
                "deviceId": station["station_id"],
                "name": station["name"],
                "district": station["district"],
                "latitude": station["latitude"],
                "longitude": station["longitude"],
                "observedAt": _observed_at(air_time),
                "timestamp": _observed_at(air_time),
                "pm25": pm25,
                "pm10": _number(air_current.get("pm10")),
                "no2": _number(air_current.get("nitrogen_dioxide")),
                "so2": _number(air_current.get("sulphur_dioxide")),
                "co": (
                    round(_number(air_current.get("carbon_monoxide")) / 1000, 3)
                    if _number(air_current.get("carbon_monoxide")) is not None else None
                ),
                "o3": _number(air_current.get("ozone")),
                "aqi": calculate_cpcb_aqi(pm25) if pm25 is not None else None,
                "aqiUS": us_aqi,
                "aqiEuropean": _number(air_current.get("european_aqi")),
                "provider": "Open-Meteo Air Quality",
                "dataType": "modelled estimate",
                "aqiMethod": (
                    "CPCB PM2.5 sub-index estimate"
                    if pm25 is not None else "US AQI from Open-Meteo"
                ),
            }
            observations.append(observation)

        if weather_time:
            wind_speed_kmh = _number(weather_current.get("wind_speed_10m"))
            visibility_m = _number(weather_current.get("visibility"))
            observations.append({
                "source": "weather",
                "deviceId": station["station_id"],
                "name": station["name"],
                "district": station["district"],
                "latitude": station["latitude"],
                "longitude": station["longitude"],
                "observedAt": _observed_at(weather_time),
                "timestamp": _observed_at(weather_time),
                "temperatureC": _number(weather_current.get("temperature_2m")),
                "apparentTemperatureC": _number(weather_current.get("apparent_temperature")),
                "humidityPct": _number(weather_current.get("relative_humidity_2m")),
                "windSpeedMs": round(wind_speed_kmh / 3.6, 2) if wind_speed_kmh is not None else None,
                "windDirectionDeg": _number(weather_current.get("wind_direction_10m")),
                "dewPointC": _number(weather_current.get("dew_point_2m")),
                "weatherCode": _number(weather_current.get("weather_code")),
                "pressure": _number(weather_current.get("surface_pressure")),
                "visibility": round(visibility_m / 1000, 2) if visibility_m is not None else None,
                "rain": _number(weather_current.get("precipitation")),
                "uvIndex": _number(weather_current.get("uv_index")),
                "sunrise": (weather.get("daily") or {}).get("sunrise", [None])[0],
                "sunset": (weather.get("daily") or {}).get("sunset", [None])[0],
                "provider": "Open-Meteo Weather",
                "dataType": "modelled estimate",
            })

    return observations


def _openweathermap_station_observations(station, weather, air):
    if not isinstance(weather, dict) or not isinstance(air, dict):
        raise LiveDataUnavailable("OpenWeatherMap returned an invalid response")

    weather_current = weather.get("main") or {}
    wind = weather.get("wind") or {}
    conditions = weather.get("weather") or []
    system = weather.get("sys") or {}
    rain = weather.get("rain") or {}
    air_items = air.get("list") or []

    if (
        not isinstance(weather_current, dict)
        or not isinstance(wind, dict)
        or not isinstance(conditions, list)
        or not isinstance(system, dict)
        or not isinstance(rain, dict)
        or not isinstance(air_items, list)
        or not air_items
        or not isinstance(air_items[0], dict)
    ):
        raise LiveDataUnavailable("OpenWeatherMap returned an incomplete station response")

    condition = conditions[0] if conditions and isinstance(conditions[0], dict) else {}
    air_current = air_items[0]
    components = air_current.get("components") or {}
    air_main = air_current.get("main") or {}

    weather_time = _observed_at_unix(weather.get("dt"))
    air_time = _observed_at_unix(air_current.get("dt"))
    if (
        not weather_time
        or not air_time
        or _number(weather_current.get("temp")) is None
        or not isinstance(components, dict)
        or not components
        or not isinstance(air_main, dict)
    ):
        raise LiveDataUnavailable("OpenWeatherMap returned an incomplete station response")

    pm25 = _number(components.get("pm2_5"))
    if pm25 is None:
        raise LiveDataUnavailable("OpenWeatherMap air-pollution response has no PM2.5 value")

    observations = [{
        "source": "aq_station",
        "deviceId": station["station_id"],
        "name": station["name"],
        "district": station["district"],
        "latitude": station["latitude"],
        "longitude": station["longitude"],
        "observedAt": air_time,
        "timestamp": air_time,
        "pm25": pm25,
        "pm10": _number(components.get("pm10")),
        "no": _number(components.get("no")),
        "no2": _number(components.get("no2")),
        "so2": _number(components.get("so2")),
        "co": (
            round(_number(components.get("co")) / 1000, 3)
            if _number(components.get("co")) is not None else None
        ),
        "o3": _number(components.get("o3")),
        "nh3": _number(components.get("nh3")),
        "aqi": calculate_cpcb_aqi(pm25),
        "aqiOpenWeather": _number(air_main.get("aqi")),
        "provider": "OpenWeatherMap Air Pollution",
        "dataType": "provider estimate",
        "aqiMethod": "CPCB PM2.5 sub-index estimate",
    }]

    observations.append({
        "source": "weather",
        "deviceId": station["station_id"],
        "name": station["name"],
        "district": station["district"],
        "latitude": station["latitude"],
        "longitude": station["longitude"],
        "observedAt": weather_time,
        "timestamp": weather_time,
        "temperatureC": _number(weather_current.get("temp")),
        "apparentTemperatureC": _number(weather_current.get("feels_like")),
        "humidityPct": _number(weather_current.get("humidity")),
        "windSpeedMs": _number(wind.get("speed")),
        "windDirectionDeg": _number(wind.get("deg")),
        "weatherCode": _number(condition.get("id")),
        "weatherMain": condition.get("main"),
        "weatherDescription": condition.get("description"),
        "pressure": _number(weather_current.get("pressure")),
        "visibility": (
            round(_number(weather.get("visibility")) / 1000, 2)
            if _number(weather.get("visibility")) is not None else None
        ),
        "rain": _number(rain.get("1h")),
        "rainUnit": "mm/h",
        "sunrise": _observed_at_unix(system.get("sunrise")),
        "sunset": _observed_at_unix(system.get("sunset")),
        "provider": "OpenWeatherMap Current Weather",
        "dataType": "provider estimate",
    })
    return observations


def _fetch_openweathermap_current(stations, api_key):
    def fetch_station(station):
        location = {
            "lat": station["latitude"],
            "lon": station["longitude"],
            "appid": api_key,
        }
        weather = _request_json(
            "https://api.openweathermap.org/data/2.5/weather",
            {**location, "units": "metric"},
            "OpenWeatherMap",
        )
        air = _request_json(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            location,
            "OpenWeatherMap",
        )
        if not isinstance(weather, dict) or not isinstance(air, dict):
            raise LiveDataUnavailable("OpenWeatherMap returned an invalid response")
        return _openweathermap_station_observations(station, weather, air)

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_station, stations))
    return [observation for station_observations in results for observation in station_observations]


def get_live_observations():
    """Return cached provider observations, refreshing on a provider-appropriate interval."""
    global _cached_at, _cached_observations

    with _cache_lock:
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "").strip()
        if _cached_observations:
            uses_openweathermap = any(
                observation.get("provider", "").startswith("OpenWeatherMap")
                for observation in _cached_observations
            )
            cache_seconds = _OPENWEATHER_CACHE_SECONDS if uses_openweathermap else _CACHE_SECONDS
            if time.monotonic() - _cached_at < cache_seconds:
                return [dict(observation) for observation in _cached_observations]

        stations = fetch_stations()
        if not stations:
            raise LiveDataUnavailable("No monitoring station locations are configured")

        try:
            try:
                observations = _fetch_openmeteo_current(stations)
            except LiveDataUnavailable:
                if not api_key:
                    raise
                _LOGGER.warning("Open-Meteo request failed; using OpenWeatherMap fallback")
                observations = _fetch_openweathermap_current(stations, api_key)
        except LiveDataUnavailable:
            if _cached_observations:
                return [
                    {**observation, "stale": True}
                    for observation in _cached_observations
                ]
            raise

        _cached_observations = observations
        _cached_at = time.monotonic()
        return [dict(observation) for observation in observations]


def latest_observations(source=None, limit=500):
    """Merge live provider data with ingested records, keeping the newest per device."""
    stored = fetch_latest_observations(source=source, limit=limit)
    try:
        live = get_live_observations()
    except LiveDataUnavailable:
        if stored:
            return stored[:limit]
        raise

    if source:
        live = [observation for observation in live if observation["source"] == source]

    by_device = {observation["deviceId"]: observation for observation in live}
    for observation in stored:
        current = by_device.get(observation["deviceId"])
        if current is None or _timestamp_key(observation) > _timestamp_key(current):
            by_device[observation["deviceId"]] = observation

    return sorted(
        by_device.values(),
        key=_timestamp_key,
        reverse=True,
    )[:limit]
