"""
Export & Executive Report Endpoints for Class Presentation Demo.
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone
import ai_service
from database import fetch_stations, fetch_cml_links, fetch_active_alerts

export_bp = Blueprint("export", __name__)

@export_bp.route("/api/v1/export/report", methods=["GET"])
def export_airshed_report():
    stations = fetch_stations()
    cml_links = fetch_cml_links()
    alerts = fetch_active_alerts()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Calculate average airshed PM2.5 and identify top hotspot
    total_pm = sum(s.get("base_pm25", 35.0) for s in stations)
    avg_pm = round(total_pm / max(1, len(stations)), 1)
    avg_aqi = ai_service.calculate_cpcb_aqi(avg_pm)

    hotspot = max(stations, key=lambda s: s.get("base_pm25", 0))

    grap_stage = "NORMAL"
    if avg_aqi > 200:
        grap_stage = "GRAP STAGE I"
    elif avg_aqi > 300:
        grap_stage = "GRAP STAGE II"
    elif avg_aqi > 400:
        grap_stage = "GRAP STAGE III/IV"

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
                "activeMicrowaveLinksCount": len(cml_links),
                "highestPollutionHotspot": {
                    "name": hotspot["name"],
                    "stationId": hotspot["station_id"],
                    "basePM25": hotspot["base_pm25"],
                    "district": hotspot["district"]
                }
            },
            "aiEngineMetrics": {
                "engineLoaded": ai_service.engine_loaded,
                "modelVersion": ai_service.model_version,
                "architecture": "PyTorch Bi-Directional GRU + Multi-Horizon Quantile Suite + Isolation Forest",
                "leadTimesEvaluated": ["1h", "3h", "6h", "12h", "24h", "72h"],
                "uncertaintyQuantiles": ["P10 (Optimistic)", "P50 (Median)", "P90 (Conservative)"]
            },
            "recentAlerts": alerts
        }
    })
