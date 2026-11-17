"""
Stations routes for AeroSense API.
"""
from flask import Blueprint, jsonify, request
from database import fetch_stations, fetch_station, fetch_latest_observation
import ai_service
import time
import math

stations_bp = Blueprint("stations", __name__)

@stations_bp.route("/api/v1/stations", methods=["GET"])
def get_stations():
    stations = fetch_stations()
    # Format according to frontend expectations
    formatted = []
    sec = time.time()
    jitter = round(math.sin(sec / 2.5) * 1.5 + math.cos(sec / 1.2) * 0.9, 1)

    for s in stations:
        st_id = s["station_id"]
        base_pm = s.get("base_pm25") or 38.0
        cur_pm = max(10.0, round(base_pm + jitter, 1))
        cur_aqi = ai_service.calculate_cpcb_aqi(cur_pm)

        formatted.append({
            "id": st_id,
            "stationId": st_id,
            "name": s["name"],
            "district": s["district"],
            "type": s["station_type"],
            "lat": s["latitude"],
            "lon": s["longitude"],
            "latitude": s["latitude"],
            "longitude": s["longitude"],
            "basePM25": base_pm,
            "currentPM25": cur_pm,
            "currentAQI": cur_aqi,
            "active": bool(s["active"])
        })

    return jsonify({"data": formatted})


@stations_bp.route("/api/v1/stations/<station_id>", methods=["GET"])
def get_single_station(station_id):
    st = fetch_station(station_id)
    if not st:
        return jsonify({"error": {"message": f"Station '{station_id}' not found"}}), 404

    latest = fetch_latest_observation(station_id, "aq_station")
    return jsonify({
        "data": {
            "id": st["station_id"],
            "stationId": st["station_id"],
            "name": st["name"],
            "district": st["district"],
            "type": st["station_type"],
            "lat": st["latitude"],
            "lon": st["longitude"],
            "basePM25": st["base_pm25"],
            "active": bool(st["active"])
        },
        "latest": latest
    })
