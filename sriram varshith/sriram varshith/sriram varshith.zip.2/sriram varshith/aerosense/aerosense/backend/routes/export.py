"""
Export & Executive Report Endpoints for Class Presentation Demo.
"""
from flask import Blueprint, current_app, jsonify
from datetime import datetime, timezone
import ai_service
from database import fetch_stations, fetch_cml_links
from live_data import LiveDataUnavailable, latest_observations

export_bp = Blueprint("export", __name__)

@export_bp.route("/api/v1/export/report", methods=["GET"])
def export_airshed_report():
    stations = fetch_stations()
    cml_links = fetch_cml_links()
    try:
        aq_observations = latest_observations(source="aq_station")
    except LiveDataUnavailable as error:
        current_app.logger.error("Could not retrieve live report observations: %s", error)
        return jsonify({"error": {"message": str(error), "statusCode": 502}}), 502
    now_iso = datetime.now(timezone.utc).isoformat()

    pm25_readings = [
        observation for observation in aq_observations
        if observation.get("pm25") is not None
    ]
    avg_pm = round(sum(item["pm25"] for item in pm25_readings) / len(pm25_readings), 1) if pm25_readings else None
    avg_aqi = ai_service.calculate_cpcb_aqi(avg_pm) if avg_pm is not None else None
    hotspot = max(pm25_readings, key=lambda item: item["pm25"], default=None)
    stations_by_id = {station["station_id"]: station for station in stations}

    grap_stage = "NORMAL"
    if avg_aqi is not None and avg_aqi > 400:
        grap_stage = "GRAP STAGE III/IV"
    elif avg_aqi is not None and avg_aqi > 300:
        grap_stage = "GRAP STAGE II"
    elif avg_aqi is not None and avg_aqi > 200:
        grap_stage = "GRAP STAGE I"

    alerts = [
        {
            "deviceId": item["deviceId"],
            "pm25": item["pm25"],
            "observedAt": item["observedAt"],
        }
        for item in pm25_readings
        if item["pm25"] >= 91
    ]
    hotspot_station = stations_by_id.get(hotspot["deviceId"], {}) if hotspot else {}

    return jsonify({
        "report": {
            "title": "AeroSense Greater Noida & Delhi-NCR Airshed Executive Intelligence Report",
            "generatedAt": now_iso,
            "region": "Delhi-NCR & Greater Noida Tech / Industrial Corridor",
            "executiveSummary": {
                "regionalAveragePM25": avg_pm,
                "regionalAverageAQI": avg_aqi,
                "grapEnforcementStage": grap_stage,
                "monitoredStationsCount": len(stations),
                "stationsWithReadingsCount": len(pm25_readings),
                "activeMicrowaveLinksCount": len(cml_links),
                "highestPollutionHotspot": ({
                    "name": hotspot_station.get("name", hotspot["deviceId"]),
                    "stationId": hotspot["deviceId"],
                    "pm25": hotspot["pm25"],
                    "district": hotspot_station.get("district"),
                    "observedAt": hotspot["observedAt"],
                } if hotspot else None)
            },
            "aiEngineMetrics": {
                "engineLoaded": ai_service.engine_loaded,
                "modelVersion": ai_service.model_version,
            },
            "recentAlerts": alerts
        }
    })
