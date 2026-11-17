"""
AeroSense SQLite Database Management & Data Access Layer.
Provides ACID persistence with zero external dependencies (no MongoDB or Redis required).
"""
import sqlite3
import json
import os
from datetime import datetime, timezone
from config import DB_PATH

def get_db():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes database tables and default indices."""
    conn = get_db()
    cursor = conn.cursor()

    # Stations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stations (
        station_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        district TEXT,
        station_type TEXT,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        base_pm25 REAL DEFAULT 35.0,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Commercial Microwave Links table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cml_links (
        link_id TEXT PRIMARY KEY,
        from_tower TEXT NOT NULL,
        from_lat REAL,
        from_lon REAL,
        to_tower TEXT NOT NULL,
        to_lat REAL,
        to_lon REAL,
        frequency_ghz REAL NOT NULL,
        baseline_rsl_dbm REAL NOT NULL,
        polarization TEXT DEFAULT 'H',
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Observations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        device_id TEXT NOT NULL,
        observed_at TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        pm25 REAL,
        pm10 REAL,
        no2 REAL,
        so2 REAL,
        co REAL,
        o3 REAL,
        temperature_c REAL,
        humidity_pct REAL,
        wind_speed_ms REAL,
        wind_dir_deg REAL,
        pressure_hpa REAL,
        visibility_km REAL,
        rainfall_mm REAL,
        rsl_dbm REAL,
        frequency_ghz REAL,
        quality REAL DEFAULT 1.0,
        raw_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Alerts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        severity TEXT NOT NULL,
        device_id TEXT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        observed_at TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Telemetry sync logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_sync_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        synced_at TEXT NOT NULL,
        mode TEXT,
        stations_updated INTEGER,
        weather_synced INTEGER
    );
    """)

    # Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_source_device ON observations(source, device_id, observed_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_time ON observations(observed_at DESC);")

    conn.commit()
    conn.close()
    print(f"[Database] SQLite schema verified at {DB_PATH}")

def fetch_stations(active_only=True):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM stations" + (" WHERE active = 1" if active_only else "") + " ORDER BY name ASC"
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def fetch_station(station_id):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM stations WHERE station_id = ?", (station_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def fetch_cml_links(active_only=True):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM cml_links" + (" WHERE active = 1" if active_only else "") + " ORDER BY link_id ASC"
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def fetch_latest_observation(device_id, source=None):
    conn = get_db()
    cursor = conn.cursor()
    if source:
        query = "SELECT * FROM observations WHERE device_id = ? AND source = ? ORDER BY observed_at DESC LIMIT 1"
        row = cursor.execute(query, (device_id, source)).fetchone()
    else:
        query = "SELECT * FROM observations WHERE device_id = ? ORDER BY observed_at DESC LIMIT 1"
        row = cursor.execute(query, (device_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def insert_observation_record(obs):
    conn = get_db()
    cursor = conn.cursor()
    now_iso = obs.get("observed_at") or obs.get("observedAt") or obs.get("timestamp") or datetime.now(timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO observations (
        source, device_id, observed_at, latitude, longitude,
        pm25, pm10, no2, so2, co, o3,
        temperature_c, humidity_pct, wind_speed_ms, wind_dir_deg,
        pressure_hpa, visibility_km, rainfall_mm,
        rsl_dbm, frequency_ghz, quality, raw_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        obs.get("source"),
        obs.get("device_id") or obs.get("deviceId"),
        now_iso,
        obs.get("latitude") or obs.get("lat"),
        obs.get("longitude") or obs.get("lon"),
        obs.get("pm25"),
        obs.get("pm10"),
        obs.get("no2"),
        obs.get("so2"),
        obs.get("co"),
        obs.get("o3"),
        obs.get("temperature_c") or obs.get("temperatureC") or obs.get("temp"),
        obs.get("humidity_pct") or obs.get("humidityPct") or obs.get("relativeHumidity"),
        obs.get("wind_speed_ms") or obs.get("windSpeedMs") or obs.get("windSpeed"),
        obs.get("wind_dir_deg") or obs.get("windDirectionDeg") or obs.get("windDir"),
        obs.get("pressure_hpa") or obs.get("pressure"),
        obs.get("visibility_km") or obs.get("visibility"),
        obs.get("rainfall_mm") or obs.get("rain") or obs.get("rainfallMmHr"),
        obs.get("rsl_dbm") or obs.get("rslDbm"),
        obs.get("frequency_ghz") or obs.get("frequencyGhz"),
        obs.get("quality", 1.0),
        json.dumps(obs)
    ))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def fetch_active_alerts():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    return [dict(r) for r in rows]
