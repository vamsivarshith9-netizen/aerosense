#!/usr/bin/env python3
"""
AeroSense Backend Launcher (Top Level).
Run this script to launch the Python Flask API from the root directory.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Find backend directory
BACKEND_DIR = os.path.join(BASE_DIR, "aerosense", "aerosense", "backend")
if not os.path.exists(BACKEND_DIR):
    BACKEND_DIR = os.path.join(BASE_DIR, "aerosense", "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.chdir(BACKEND_DIR)

from app import app
import config
import ai_service

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AeroSense Flask Backend Server")
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

    app.run(host=args.host, port=args.port, debug=config.DEBUG)
