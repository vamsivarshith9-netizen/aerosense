"""
AeroSense Backend Configuration Module.
Supports environment variables, command-line arguments, and intelligent path resolution.
"""
import os
import sys

# Base directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)  # aerosense/aerosense

# Resolve ai/saved_models directory
def resolve_models_dir():
    candidates = [
        os.path.join(PROJECT_ROOT, "ai", "saved_models"),
        os.path.join(BACKEND_DIR, "ai", "saved_models"),
        os.path.join(PROJECT_ROOT, "aerosense-backend", "ml-service", "ai", "saved_models"),
        os.path.abspath("ai/saved_models"),
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.isdir(p):
            return p
    return candidates[0]

MODELS_DIR = resolve_models_dir()

# Server settings
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")

# Database settings
DB_PATH = os.environ.get("DB_PATH", os.path.join(BACKEND_DIR, "aerosense.db"))

# CORS settings
CORS_ORIGINS = os.environ.get("CORS_ORIGIN", "*").split(",")
