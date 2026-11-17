"""
Predictions and ML Forecasting endpoints.
Proxies to CoupledLiveEngine or runs baseline atmospheric fusion.
"""
from flask import Blueprint, jsonify, request
import ai_service

predictions_bp = Blueprint("predictions", __name__)

@predictions_bp.route("/api/v1/predictions", methods=["POST"])
@predictions_bp.route("/v1/forecast", methods=["POST"])
def get_prediction():
    payload = request.get_json(silent=True) or {}
    station_id = payload.get("stationId") or payload.get("station_id") or "ncr_gnoida_kp3"
    features = payload.get("features") or {}
    horizons = payload.get("horizons")

    # If horizonHours is supplied instead of array
    if horizons is None and payload.get("horizonHours") is not None:
        horizons = list(range(min(73, int(payload["horizonHours"]) + 1)))

    forecast_data = ai_service.generate_forecast(
        station_id=station_id,
        features=features,
        horizons=horizons
    )

    return jsonify({"data": forecast_data})
