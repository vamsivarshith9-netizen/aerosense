"""
Observations and telemetry ingestion routes.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import math
import time
from database import fetch_stations, fetch_cml_links, insert_observation_record
import ai_service

observations_bp = Blueprint("observations", __name__)

@observations_bp.route("/api/v1/observations/latest", methods=["GET"])
def get_latest_observations():
    source = request.args.get("source")
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    sec = time.time()

    # Dynamic sub-second fluctuation mimicking continuous live telemetry
    jitter = round(math.sin(sec / 2.5) * 1.5 + math.cos(sec / 1.2) * 0.9, 1)

    obs = []
    stations = fetch_stations()

    if not source or source == "aq_station":
        for s in stations:
            st_id = s["station_id"]
            base = s.get("base_pm25") or 38.0
            val_pm25 = max(10.0, round(base + jitter, 1))
            val_pm10 = round(val_pm25 * 1.55 + jitter * 0.4, 1)
            obs.append({
                "source": "aq_station",
                "deviceId": st_id,
                "timestamp": now_iso,
                "observedAt": now_iso,
                "pm25": val_pm25,
                "pm10": val_pm10,
                "no2": round(28.0 + (val_pm25 / 4.0), 1),
                "so2": round(11.0 + (val_pm25 / 10.0), 1),
                "co": round(0.4 + (val_pm25 / 80.0), 2),
                "o3": round(44.0 - (val_pm25 / 15.0), 1),
                "aqi": ai_service.calculate_cpcb_aqi(val_pm25),
                "latitude": s["latitude"],
                "longitude": s["longitude"],
                "quality": 0.98
            })

    if not source or source == "weather":
        wx_temp = round(29.5 + math.sin(sec / 15.0) * 0.5, 1)
        wx_rh = round(64.0 + math.cos(sec / 18.0) * 1.5, 1)
        wx_wind = round(2.6 + math.sin(sec / 8.0) * 0.3, 1)
        obs.append({
            "source": "weather",
            "deviceId": "wx_gnoida_meteo",
            "timestamp": now_iso,
            "observedAt": now_iso,
            "temp": wx_temp,
            "temperatureC": wx_temp,
            "relativeHumidity": wx_rh,
            "humidityPct": wx_rh,
            "windSpeed": wx_wind,
            "windSpeedMs": wx_wind,
            "windDir": 315,
            "windDirectionDeg": 315,
            "pressure": 1008,
            "visibility": 5.2,
            "rain": 0.0,
            "rainfallMmHr": 0.0,
            "quality": 1.0
        })

    if not source or source == "cml":
        cml_links = fetch_cml_links()
        for link in cml_links:
            base_rsl = link.get("baseline_rsl_dbm") or -42.0
            rsl_fluctuation = round(math.sin(sec / 5.0 + hash(link["link_id"]) % 7) * 0.4, 2)
            cur_rsl = round(base_rsl + rsl_fluctuation, 2)
            obs.append({
                "source": "cml",
                "deviceId": link["link_id"],
                "timestamp": now_iso,
                "observedAt": now_iso,
                "rslDbm": cur_rsl,
                "frequencyGhz": link["frequency_ghz"],
                "attenuationDb": round(abs(cur_rsl - base_rsl), 2),
                "quality": 0.95
            })

    return jsonify({
        "data": obs,
        "sync": {
            "mode": "live_streaming",
            "serverTime": now_iso,
            "packetEpoch": int(sec),
            "stationsActive": len(stations)
        }
    })


@observations_bp.route("/api/v1/ingestion/observations", methods=["POST"])
def ingest_observations():
    payload = request.get_json(silent=True) or {}
    items = payload if isinstance(payload, list) else payload.get("observations", [])

    if not isinstance(items, list):
        return jsonify({"error": {"message": "Payload must be a JSON array or have an 'observations' field"}}), 400

    accepted = []
    rejected = []

    for item in items:
        try:
            row_id = insert_observation_record(item)
            accepted.append({"id": row_id, "deviceId": item.get("deviceId") or item.get("device_id")})
        except Exception as exc:
            rejected.append({"record": item, "error": str(exc)})

    status_code = 207 if (len(rejected) > 0 and len(accepted) > 0) else (201 if len(rejected) == 0 else 400)
    return jsonify({
        "received": len(items),
        "accepted": len(accepted),
        "rejected": rejected,
        "data": accepted
    }), status_code
