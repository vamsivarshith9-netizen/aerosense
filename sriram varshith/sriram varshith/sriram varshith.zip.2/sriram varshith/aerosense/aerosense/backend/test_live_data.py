import os
import unittest
from unittest.mock import patch

import live_data


STATION = {
    "station_id": "test_station",
    "name": "Test Station",
    "district": "Test District",
    "latitude": 28.4,
    "longitude": 77.5,
}

WEATHER = {
    "dt": 1606147200,
    "main": {
        "temp": 21.5,
        "feels_like": 20.2,
        "pressure": 1012,
        "humidity": 54,
    },
    "wind": {"speed": 2.4, "deg": 280},
    "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}],
    "visibility": 9000,
    "rain": {"1h": 0.2},
    "sys": {"sunrise": 1606110000, "sunset": 1606150000},
}

AIR = {
    "list": [{
        "dt": 1606147200,
        "main": {"aqi": 3},
        "components": {
            "co": 3200,
            "no": 1.2,
            "no2": 32.4,
            "o3": 50,
            "so2": 12,
            "pm2_5": 40.1,
            "pm10": 52,
            "nh3": 1.1,
        },
    }],
}


class LiveDataTests(unittest.TestCase):
    def setUp(self):
        self.cached_at = live_data._cached_at
        self.cached_observations = live_data._cached_observations
        live_data._cached_at = 0
        live_data._cached_observations = []

    def tearDown(self):
        live_data._cached_at = self.cached_at
        live_data._cached_observations = self.cached_observations

    def test_openweathermap_maps_provider_weather_and_air_data(self):
        def request(url, _params, _provider):
            return WEATHER if url.endswith("/weather") else AIR

        with patch("live_data._request_json", side_effect=request):
            observations = live_data._fetch_openweathermap_current([STATION], "test-key")

        air = next(item for item in observations if item["source"] == "aq_station")
        weather = next(item for item in observations if item["source"] == "weather")
        self.assertEqual(air["pm25"], 40.1)
        self.assertEqual(air["aqiOpenWeather"], 3)
        self.assertEqual(air["no"], 1.2)
        self.assertEqual(air["nh3"], 1.1)
        self.assertEqual(air["co"], 3.2)
        self.assertEqual(air["provider"], "OpenWeatherMap Air Pollution")
        self.assertEqual(weather["temperatureC"], 21.5)
        self.assertEqual(weather["apparentTemperatureC"], 20.2)
        self.assertEqual(weather["rain"], 0.2)
        self.assertEqual(weather["rainUnit"], "mm/h")
        self.assertEqual(weather["provider"], "OpenWeatherMap Current Weather")

    def test_openmeteo_failure_uses_openweathermap_fallback(self):
        fallback = [{"source": "weather", "deviceId": STATION["station_id"]}]
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"}), \
                patch("live_data.fetch_stations", return_value=[STATION]), \
                patch(
                    "live_data._fetch_openmeteo_current",
                    side_effect=live_data.LiveDataUnavailable("provider unavailable"),
                ), \
                patch("live_data._fetch_openweathermap_current", return_value=fallback) as openweathermap:
            observations = live_data.get_live_observations()

        self.assertEqual(observations, fallback)
        openweathermap.assert_called_once_with([STATION], "test-key")

    def test_openmeteo_is_primary_when_openweathermap_key_is_configured(self):
        primary = [{"source": "weather", "deviceId": STATION["station_id"]}]
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"}), \
                patch("live_data.fetch_stations", return_value=[STATION]), \
                patch("live_data._fetch_openmeteo_current", return_value=primary) as openmeteo, \
                patch("live_data._fetch_openweathermap_current") as openweathermap:
            observations = live_data.get_live_observations()

        self.assertEqual(observations, primary)
        openmeteo.assert_called_once_with([STATION])
        openweathermap.assert_not_called()

    def test_openmeteo_keeps_us_aqi_when_pm25_is_unavailable(self):
        weather = {
            "current": {
                "time": "2026-11-16T20:00",
                "temperature_2m": 19.0,
            },
            "daily": {},
        }
        air = {
            "current": {
                "time": "2026-11-16T20:00",
                "pm2_5": None,
                "us_aqi": 142,
                "european_aqi": 61,
            },
        }

        def request(url, _params, _provider="Open-Meteo"):
            return air if "air-quality-api" in url else weather

        with patch("live_data._request_json", side_effect=request):
            observations = live_data._fetch_openmeteo_current([STATION])

        air_observation = next(item for item in observations if item["source"] == "aq_station")
        self.assertIsNone(air_observation["pm25"])
        self.assertIsNone(air_observation["aqi"])
        self.assertEqual(air_observation["aqiUS"], 142)
        self.assertEqual(air_observation["aqiMethod"], "US AQI from Open-Meteo")


if __name__ == "__main__":
    unittest.main()
