"""
AeroSense Python Flask API Application.
Main entry point for the backend services.
"""
import os
import sys
import argparse
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

import config
from database import init_db
from seed_data import seed_database_if_needed
from routes import (
    health_bp,
    dashboard_bp,
    stations_bp,
    observations_bp,
    weather_bp,
    cml_bp,
    predictions_bp,
    telemetry_bp,
    export_bp
)
import ai_service


def create_app():
    """Application factory for AeroSense Flask API."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # Enable Cross-Origin Resource Sharing for all origins
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize SQLite database and auto-seed reference data
    init_db()
    seed_database_if_needed()

    # Register API blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(observations_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(cml_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(telemetry_bp)
    app.register_blueprint(export_bp)

    # Root landing dashboard for classroom demonstration
    @app.route("/", methods=["GET"])
    def root_index():
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AEROSENSE Python Flask API Server</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body { font-family: 'Outfit', sans-serif; }
                code, pre { font-family: 'JetBrains Mono', monospace; }
            </style>
        </head>
        <body class="bg-slate-950 text-slate-100 min-h-screen p-6 sm:p-12 flex flex-col justify-between">
            <div class="max-w-4xl mx-auto w-full">
                <!-- Header -->
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-8 border-b border-slate-800 gap-4">
                    <div>
                        <div class="flex items-center gap-3">
                            <span class="text-3xl font-extrabold tracking-wider bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">AEROSENSE</span>
                            <span class="px-3 py-1 rounded-full text-xs font-bold tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                                FLASK API ONLINE
                            </span>
                        </div>
                        <p class="text-slate-400 text-sm mt-1">Hyper-Local Atmospheric & Air Quality Intelligence Engine</p>
                    </div>
                    <div class="text-right">
                        <span class="text-xs text-slate-400">Classroom Presentation Build</span>
                        <div class="text-sm font-semibold text-slate-300">Port {{ port }} • SQLite Active</div>
                    </div>
                </div>

                <!-- AI Status Cards -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 my-8">
                    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
                        <div class="text-xs uppercase font-bold text-slate-400">AI Forecasting Tier</div>
                        <div class="text-lg font-bold text-sky-400 mt-1 flex items-center gap-2">
                            <span>PyTorch Bi-GRU</span>
                            <span class="text-[10px] bg-sky-950 text-sky-300 px-2 py-0.5 rounded border border-sky-800">72h Trajectory</span>
                        </div>
                        <p class="text-xs text-slate-400 mt-2">Continuous multi-step sequence modeling of atmospheric boundary dynamics.</p>
                    </div>

                    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
                        <div class="text-xs uppercase font-bold text-slate-400">Uncertainty Bounds</div>
                        <div class="text-lg font-bold text-emerald-400 mt-1 flex items-center gap-2">
                            <span>Quantiles [P10, P50, P90]</span>
                        </div>
                        <p class="text-xs text-slate-400 mt-2">HistGradientBoosting regressors guarding strict mathematical monotonicity.</p>
                    </div>

                    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
                        <div class="text-xs uppercase font-bold text-slate-400">CML Microwave Sensing</div>
                        <div class="text-lg font-bold text-amber-400 mt-1 flex items-center gap-2">
                            <span>25 Cellular Links</span>
                        </div>
                        <p class="text-xs text-slate-400 mt-2">ITU-R P.838-3 specific attenuation coupling microwave signals with particulate load.</p>
                    </div>
                </div>

                <!-- Quick Test Buttons -->
                <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 mb-8">
                    <h3 class="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center gap-2">
                        <span>⚡ Interactive Endpoint Verification</span>
                        <span class="text-xs text-slate-500 font-normal">(Click to verify live responses)</span>
                    </h3>
                    <div class="flex flex-wrap gap-3">
                        <a href="/health" target="_blank" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-xl text-xs font-mono font-bold transition flex items-center gap-1.5 border border-slate-700">
                            <span>GET</span> /health
                        </a>
                        <a href="/api/v1/dashboard" target="_blank" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-xl text-xs font-mono font-bold transition flex items-center gap-1.5 border border-slate-700">
                            <span>GET</span> /api/v1/dashboard
                        </a>
                        <a href="/api/v1/stations" target="_blank" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-xl text-xs font-mono font-bold transition flex items-center gap-1.5 border border-slate-700">
                            <span>GET</span> /api/v1/stations
                        </a>
                        <a href="/api/v1/weather" target="_blank" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-xl text-xs font-mono font-bold transition flex items-center gap-1.5 border border-slate-700">
                            <span>GET</span> /api/v1/weather
                        </a>
                        <a href="/api/v1/observations/latest?source=aq_station" target="_blank" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-xl text-xs font-mono font-bold transition flex items-center gap-1.5 border border-slate-700">
                            <span>GET</span> /api/v1/observations/latest
                        </a>
                        <a href="/api/v1/cml/links" target="_blank" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-xl text-xs font-mono font-bold transition flex items-center gap-1.5 border border-slate-700">
                            <span>GET</span> /api/v1/cml/links
                        </a>
                        <a href="/api/v1/export/report" target="_blank" class="px-4 py-2 bg-indigo-900/60 hover:bg-indigo-800 text-indigo-300 rounded-xl text-xs font-mono font-bold transition flex items-center gap-1.5 border border-indigo-700">
                            <span>GET</span> /api/v1/export/report
                        </a>
                    </div>
                </div>

                <!-- Launch UI helper -->
                <div class="bg-gradient-to-r from-sky-950/60 to-indigo-950/60 border border-sky-800/40 rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div>
                        <div class="text-sm font-bold text-sky-200">Ready to present the frontend dashboard?</div>
                        <p class="text-xs text-slate-400 mt-1">Make sure the frontend is running on port 5173 to view the 360° atmospheric radar and live telemetry cards.</p>
                    </div>
                    <a href="http://localhost:5173" target="_blank" class="px-5 py-2.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-sm rounded-xl transition shadow-lg shrink-0">
                        Open Frontend (:5173) →
                    </a>
                </div>
            </div>

            <div class="max-w-4xl mx-auto w-full text-center text-xs text-slate-600 mt-8">
                AeroSense AI Engineering Team • Greater Noida & Delhi-NCR Air Quality Management Platform
            </div>
        </body>
        </html>
        """
        return render_template_string(html_content, port=config.PORT)

    # 404 Handler
    @app.errorhandler(404)
    def not_found_handler(err):
        return jsonify({"error": {"message": "Resource not found", "statusCode": 404}}), 404

    # 500 Handler
    @app.errorhandler(500)
    def internal_error_handler(err):
        return jsonify({"error": {"message": "Internal server error", "statusCode": 500}}), 500

    return app


app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroSense Flask API Server")
    parser.add_argument("--port", type=int, default=config.PORT, help="Port to listen on (default 8000)")
    parser.add_argument("--host", type=str, default=config.HOST, help="Host to bind to (default 0.0.0.0)")
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"  🚀 AEROSENSE FLASK BACKEND SERVER STARTED")
    print(f"  📍 Host: {args.host} | Port: {args.port}")
    print(f"  📊 AI Engine: {'ONLINE (CoupledLiveEngine)' if ai_service.engine_loaded else 'Atmospheric Baseline'}")
    print(f"  🔗 Health URL: http://localhost:{args.port}/health")
    print(f"  🌐 Interactive Dashboard: http://localhost:{args.port}/")
    print(f"{'='*70}\n")

    app.run(host=args.host, port=args.port, debug=config.DEBUG, load_dotenv=False)
