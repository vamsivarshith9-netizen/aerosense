"""
Stations routes for AeroSense API.
"""
from flask import Blueprint, current_app, jsonify
from database import fetch_stations, fetch_station, fetch_latest_observation, format_observation
from live_data import LiveDataUnavailable, latest_observations

stations_bp = Blueprint("stations", __name__)

@stations_bp.route("/api/v1/stations", methods=["GET"])
def get_stations():
    stations = fetch_stations()
    formatted = [
        {
            "id": s["station_id"],
            "stationId": s["station_id"],
            "name": s["name"],
            "district": s["district"],
            "type": s["station_type"],
            "lat": s["latitude"],
            "lon": s["longitude"],
            "latitude": s["latitude"],
            "longitude": s["longitude"],
            "active": bool(s["active"])
        }
        for s in stations
    ]

    return jsonify({"data": formatted})


@stations_bp.route("/api/v1/stations/<station_id>", methods=["GET"])
def get_single_station(station_id):
    st = fetch_station(station_id)
    if not st:
        return jsonify({"error": {"message": f"Station '{station_id}' not found"}}), 404

    try:
        latest = next(
            (observation for observation in latest_observations("aq_station") if observation["deviceId"] == station_id),
            None,
        )
    except LiveDataUnavailable as error:
        current_app.logger.error("Could not retrieve live station observation: %s", error)
        return jsonify({"error": {"message": str(error), "statusCode": 502}}), 502

    if latest is None:
        latest = format_observation(fetch_latest_observation(station_id, "aq_station"))

    return jsonify({
        "data": {
            "id": st["station_id"],
            "stationId": st["station_id"],
            "name": st["name"],
            "district": st["district"],
            "type": st["station_type"],
            "lat": st["latitude"],
            "lon": st["longitude"],
            "active": bool(st["active"])
        },
        "latest": latest
    })
