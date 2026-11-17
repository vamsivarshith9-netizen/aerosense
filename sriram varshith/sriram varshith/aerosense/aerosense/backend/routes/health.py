"""
Health check endpoints for AeroSense API.
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone
import ai_service
from config import DB_PATH

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
@health_bp.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "aerosense-python-flask-api",
        "version": "2.5.0",
        "engineLoaded": ai_service.engine_loaded,
        "modelVersion": ai_service.model_version,
        "database": "sqlite3",
        "dbPath": DB_PATH,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
