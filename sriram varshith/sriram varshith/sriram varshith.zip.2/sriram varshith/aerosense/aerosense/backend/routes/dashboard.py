"""
Dashboard aggregate endpoint for AeroSense.
Combines stations, latest telemetry, alerts, and summary counts.
"""
from flask import Blueprint, current_app, jsonify
from database import fetch_stations, fetch_cml_links, fetch_latest_observations
from live_data import LiveDataUnavailable, latest_observations
import ai_service

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/api/v1/dashboard", methods=["GET"])
def get_dashboard():
    stations = [
        {
            "id": station["station_id"],
            "stationId": station["station_id"],
            "name": station["name"],
            "district": station["district"],
            "type": station["station_type"],
            "lat": station["latitude"],
            "lon": station["longitude"],
            "active": bool(station["active"]),
        }
        for station in fetch_stations()
    ]
    cml_links = fetch_cml_links()
    try:
        aq_obs = latest_observations(source="aq_station")
        weather_obs = latest_observations(source="weather")
    except LiveDataUnavailable as error:
        current_app.logger.error("Could not retrieve live dashboard observations: %s", error)
        return jsonify({"error": {"message": str(error), "statusCode": 502}}), 502

    cml_obs = fetch_latest_observations(source="cml")
    station_by_id = {station["stationId"]: station for station in stations}

    for observation in aq_obs:
        station = station_by_id.get(observation["deviceId"], {})
        observation["name"] = station.get("name")
        observation["district"] = station.get("district")
        observation["aqi"] = ai_service.calculate_cpcb_aqi(observation["pm25"]) if observation.get("pm25") is not None else None

    formatted_alerts = [
        {
            "id": f"pm25-{observation['id']}",
            "severity": "critical" if observation["pm25"] >= 121 else "warning",
            "deviceId": observation["deviceId"],
            "title": "Elevated PM2.5 reading",
            "description": f"PM2.5 is {observation['pm25']} µg/m³ at {observation['deviceId']}.",
            "message": f"PM2.5 is {observation['pm25']} µg/m³ at {observation['deviceId']}.",
            "timestamp": observation["observedAt"],
        }
        for observation in aq_obs
        if observation.get("pm25") is not None and observation["pm25"] >= 91
    ]

    return jsonify({
        "data": {
            "stations": stations,
            "observations": {
                "aq": aq_obs,
                "weather": weather_obs,
                "cml": cml_obs
            },
            "alerts": formatted_alerts,
            "summary": {
                "stationCount": len(stations),
                "activeCmlLinks": len(cml_links),
                "activeAlerts": len(formatted_alerts),
                "engineLoaded": ai_service.engine_loaded,
                "modelVersion": ai_service.model_version
            }
        }
    })
