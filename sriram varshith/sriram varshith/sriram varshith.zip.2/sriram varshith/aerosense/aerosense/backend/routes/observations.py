"""
Observations and telemetry ingestion routes.
"""
from flask import Blueprint, current_app, jsonify, request
from database import insert_observation_record
from live_data import LiveDataUnavailable, latest_observations

observations_bp = Blueprint("observations", __name__)
VALID_SOURCES = {"aq_station", "weather", "cml"}

@observations_bp.route("/api/v1/observations/latest", methods=["GET"])
def get_latest_observations():
    source = request.args.get("source")
    if source and source not in VALID_SOURCES:
        return jsonify({"error": {"message": "source must be aq_station, weather, or cml"}}), 400

    try:
        data = latest_observations(source=source)
    except LiveDataUnavailable as error:
        current_app.logger.error("Could not retrieve live observations: %s", error)
        return jsonify({"error": {"message": str(error), "statusCode": 502}}), 502

    return jsonify({"data": data})


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
