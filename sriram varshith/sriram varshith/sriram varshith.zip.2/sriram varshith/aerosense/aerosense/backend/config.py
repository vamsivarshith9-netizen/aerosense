"""
AeroSense Backend Configuration Module.
Supports environment variables, command-line arguments, and intelligent path resolution.
"""
import os
import sys

# Base directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))


def load_openweathermap_key():
    """Load the optional provider key from backend/.env without overriding the environment."""
    key_name = "OPENWEATHERMAP_API_KEY"
    if os.environ.get(key_name):
        return

    env_path = os.path.join(BACKEND_DIR, ".env")
    try:
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                name, separator, value = line.strip().partition("=")
                if name == key_name and separator:
                    value = value.strip()
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                        value = value[1:-1]
                    if value:
                        os.environ[key_name] = value
                    return
    except FileNotFoundError:
        return


load_openweathermap_key()
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
