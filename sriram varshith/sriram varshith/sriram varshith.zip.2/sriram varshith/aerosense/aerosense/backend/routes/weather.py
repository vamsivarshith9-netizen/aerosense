"""
Weather endpoints for AeroSense API.
"""
from flask import Blueprint, current_app, jsonify
from live_data import LiveDataUnavailable, latest_observations

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/api/v1/weather", methods=["GET"])
def get_current_weather():
    try:
        observations = latest_observations(source="weather")
    except LiveDataUnavailable as error:
        current_app.logger.error("Could not retrieve live weather: %s", error)
        return jsonify({"error": {"message": str(error), "statusCode": 502}}), 502

    observation = next(
        (item for item in observations if item["deviceId"] == "ncr_gnoida_kp3"),
        observations[0] if observations else None,
    )
    return jsonify({"data": observation})
