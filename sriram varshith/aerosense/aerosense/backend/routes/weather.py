"""
Weather endpoints for AeroSense API.
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone
import math
import time

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/api/v1/weather", methods=["GET"])
def get_current_weather():
    sec = time.time()
    temp = round(29.5 + math.sin(sec / 15.0) * 0.4, 1)
    humidity = round(64.0 + math.cos(sec / 18.0) * 1.5, 1)
    wind_speed = round(2.6 + math.sin(sec / 8.0) * 0.3, 1)

    return jsonify({
        "data": {
            "temp": temp,
            "temperatureC": temp,
            "relativeHumidity": humidity,
            "humidityPct": humidity,
            "windSpeed": wind_speed,
            "windSpeedMs": wind_speed,
            "windDir": 315,
            "windDirectionDeg": 315,
            "pressure": 1008,
            "visibility": 5.2,
            "rain": 0.0,
            "rainfallMmHr": 0.0,
            "solarRadiationWm2": round(max(0, 480 * math.sin((time.localtime().tm_hour - 6) * math.pi / 12)), 1),
            "mixingHeightM": 420.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
