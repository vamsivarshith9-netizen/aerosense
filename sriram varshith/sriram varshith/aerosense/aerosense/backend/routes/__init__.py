"""
AeroSense Routes Package.
"""
from .health import health_bp
from .dashboard import dashboard_bp
from .stations import stations_bp
from .observations import observations_bp
from .weather import weather_bp
from .cml import cml_bp
from .predictions import predictions_bp
from .telemetry import telemetry_bp
from .export import export_bp

__all__ = [
    "health_bp",
    "dashboard_bp",
    "stations_bp",
    "observations_bp",
    "weather_bp",
    "cml_bp",
    "predictions_bp",
    "telemetry_bp",
    "export_bp",
]
