"""
Telemetry synchronization endpoints.
"""
from flask import Blueprint, jsonify

telemetry_bp = Blueprint("telemetry", __name__)

@telemetry_bp.route("/api/v1/telemetry/sync", methods=["POST"])
def telemetry_sync():
    return jsonify({
        "error": {
            "message": "No external telemetry source is configured. Submit readings through /api/v1/ingestion/observations.",
            "statusCode": 503,
        }
    }), 503
