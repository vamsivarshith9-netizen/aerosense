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
        base_pm25 REAL,
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

def format_observation(row):
    """Return a persisted observation in the API's canonical response shape."""
    if not row:
        return None

    raw = json.loads(row.get("raw_json") or "{}")
    observation = {
        "id": row["id"],
        "source": row["source"],
        "deviceId": row["device_id"],
        "observedAt": row["observed_at"],
        "timestamp": row["observed_at"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "pm25": row["pm25"],
        "pm10": row["pm10"],
        "no2": row["no2"],
        "so2": row["so2"],
        "co": row["co"],
        "o3": row["o3"],
        "temperatureC": row["temperature_c"],
        "humidityPct": row["humidity_pct"],
        "windSpeedMs": row["wind_speed_ms"],
        "windDirectionDeg": row["wind_dir_deg"],
        "pressure": row["pressure_hpa"],
        "visibility": row["visibility_km"],
        "rain": row["rainfall_mm"],
        "rslDbm": row["rsl_dbm"],
        "frequencyGhz": row["frequency_ghz"],
        "quality": row["quality"],
    }

    # Keep provider fields that are not represented by the normalized schema.
    observation.update(raw)
    observation.update({
        "id": row["id"],
        "source": row["source"],
        "deviceId": row["device_id"],
        "observedAt": row["observed_at"],
        "timestamp": row["observed_at"],
    })
    return observation

def fetch_latest_observations(source=None, limit=500):
    """Return the newest persisted reading for each device, optionally by source."""
    safe_limit = max(1, min(int(limit or 500), 1000))
    conn = get_db()
    cursor = conn.cursor()

    if source:
        query = """
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY source, device_id ORDER BY observed_at DESC, id DESC
            ) AS row_number
            FROM observations
            WHERE source = ?
        )
        WHERE row_number = 1
        ORDER BY observed_at DESC, id DESC
        LIMIT ?
        """
        rows = cursor.execute(query, (source, safe_limit)).fetchall()
    else:
        query = """
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY source, device_id ORDER BY observed_at DESC, id DESC
            ) AS row_number
            FROM observations
        )
        WHERE row_number = 1
        ORDER BY observed_at DESC, id DESC
        LIMIT ?
        """
        rows = cursor.execute(query, (safe_limit,)).fetchall()

    conn.close()
    return [format_observation(dict(row)) for row in rows]

def insert_observation_record(obs):
    conn = get_db()
    cursor = conn.cursor()

    def first_present(*values):
        return next((value for value in values if value is not None), None)

    def field(*names):
        return first_present(*(obs.get(name) for name in names))

    location = obs.get("location") or {}
    coordinates = location.get("coordinates", []) if isinstance(location, dict) else []
    latitude = first_present(field("latitude", "lat"), coordinates[1] if len(coordinates) > 1 else None)
    longitude = first_present(field("longitude", "lon"), coordinates[0] if coordinates else None)
    observed_at = field("observed_at", "observedAt", "timestamp", "time")
    now_iso = observed_at or datetime.now(timezone.utc).isoformat()

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
        field("device_id", "deviceId", "station_id", "stationId", "link_id", "linkId"),
        now_iso,
        latitude,
        longitude,
        field("pm25", "pm2_5", "pm2.5"),
        field("pm10", "pm_10"),
        field("no2", "nitrogen_dioxide"),
        field("so2", "sulphur_dioxide"),
        field("co", "carbon_monoxide"),
        field("o3", "ozone"),
        field("temperature_c", "temperatureC", "temperature", "temp"),
        field("humidity_pct", "humidityPct", "relativeHumidity", "relative_humidity", "humidity"),
        field("wind_speed_ms", "windSpeedMs", "windSpeed", "wind_speed"),
        field("wind_dir_deg", "windDirectionDeg", "windDir", "wind_direction"),
        field("pressure_hpa", "pressureHpa", "pressure"),
        field("visibility_km", "visibilityKm", "visibility"),
        field("rainfall_mm", "rainfallMmHr", "rainfall", "rain"),
        field("rsl_dbm", "rslDbm", "rsl"),
        field("frequency_ghz", "frequencyGhz", "frequency"),
        field("quality") if field("quality") is not None else 1.0,
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
