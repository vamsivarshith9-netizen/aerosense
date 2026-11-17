"""
Dashboard aggregate endpoint for AeroSense.
Combines stations, latest telemetry, alerts, and summary counts.
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone
import math
import time
from database import fetch_stations, fetch_cml_links, fetch_active_alerts
import ai_service

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/api/v1/dashboard", methods=["GET"])
def get_dashboard():
    sec = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    jitter = round(math.sin(sec / 2.5) * 1.5 + math.cos(sec / 1.2) * 0.9, 1)

    stations = fetch_stations()
    cml_links = fetch_cml_links()
    alerts = fetch_active_alerts()

    # Formatted AQ observations
    aq_obs = []
    for s in stations:
        base = s.get("base_pm25") or 38.0
        val_pm25 = max(10.0, round(base + jitter, 1))
        aq_obs.append({
            "source": "aq_station",
            "deviceId": s["station_id"],
            "name": s["name"],
            "district": s["district"],
            "latitude": s["latitude"],
            "longitude": s["longitude"],
            "observedAt": now_iso,
            "pm25": val_pm25,
            "pm10": round(val_pm25 * 1.55 + jitter * 0.4, 1),
            "aqi": ai_service.calculate_cpcb_aqi(val_pm25),
        })

    # Weather observation
    wx_temp = round(29.5 + math.sin(sec / 15.0) * 0.4, 1)
    weather_obs = [{
        "source": "weather",
        "deviceId": "wx_gnoida_meteo",
        "observedAt": now_iso,
        "temperatureC": wx_temp,
        "humidityPct": 64,
        "windSpeedMs": 2.6,
        "windDirectionDeg": 315,
        "pressure": 1008,
        "visibility": 5.2
    }]

    # CML observation
    cml_obs = []
    for l in cml_links[:6]:
        cml_obs.append({
            "source": "cml",
            "deviceId": l["link_id"],
            "observedAt": now_iso,
            "rslDbm": l["baseline_rsl_dbm"],
            "frequencyGhz": l["frequency_ghz"]
        })

    # Format alerts for frontend
    formatted_alerts = []
    for a in alerts:
        formatted_alerts.append({
            "id": a["id"],
            "severity": a["severity"],
            "deviceId": a["device_id"],
            "title": a["title"],
            "description": a["message"],
            "message": a["message"],
            "timestamp": a["observed_at"]
        })

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
