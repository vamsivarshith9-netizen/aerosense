"""
Commercial Microwave Link (CML) endpoints.
Couples cellular backhaul attenuation with atmospheric particulate estimation.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from database import fetch_cml_links, get_db

cml_bp = Blueprint("cml", __name__)

@cml_bp.route("/api/v1/cml/links", methods=["GET"])
def get_cml_links():
    links = fetch_cml_links()
    now_iso = datetime.now(timezone.utc).isoformat()
    result = []

    for l in links:
        result.append({
            "id": l["link_id"],
            "linkId": l["link_id"],
            "from": {
                "id": l["from_tower"],
                "lat": l["from_lat"],
                "lon": l["from_lon"]
            },
            "to": {
                "id": l["to_tower"],
                "lat": l["to_lat"],
                "lon": l["to_lon"]
            },
            "frequencyGhz": l["frequency_ghz"],
            "baselineRslDbm": l["baseline_rsl_dbm"],
            "polarization": l.get("polarization", "H"),
            "health": {
                "status": "healthy",
                "score": 100,
                "lastSeenAt": now_iso
            }
        })

    return jsonify({"data": result})


@cml_bp.route("/api/v1/cml/links", methods=["POST"])
def upsert_cml_link():
    data = request.get_json(silent=True) or {}
    link_id = data.get("linkId") or data.get("link_id")
    from_info = data.get("from") or {}
    to_info = data.get("to") or {}
    freq = data.get("frequencyGhz") or data.get("frequency_ghz")
    baseline = data.get("baselineRslDbm") or data.get("baseline_rsl_dbm")

    if not link_id or freq is None or baseline is None:
        return jsonify({"error": {"message": "linkId, frequencyGhz, and baselineRslDbm are required"}}), 400

    from_tower = from_info.get("id") if isinstance(from_info, dict) else str(from_info)
    from_lat = from_info.get("lat") if isinstance(from_info, dict) else None
    from_lon = from_info.get("lon") if isinstance(from_info, dict) else None

    to_tower = to_info.get("id") if isinstance(to_info, dict) else str(to_info)
    to_lat = to_info.get("lat") if isinstance(to_info, dict) else None
    to_lon = to_info.get("lon") if isinstance(to_info, dict) else None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO cml_links (link_id, from_tower, from_lat, from_lon, to_tower, to_lat, to_lon, frequency_ghz, baseline_rsl_dbm, active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (link_id, from_tower, from_lat, from_lon, to_tower, to_lat, to_lon, float(freq), float(baseline)))
    conn.commit()
    conn.close()

    return jsonify({"status": "created", "data": {"linkId": link_id}}), 201


@cml_bp.route("/api/v1/cml/links/<link_id>/health", methods=["GET"])
def get_link_health(link_id):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM cml_links WHERE link_id = ?", (link_id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": {"message": f"CML link '{link_id}' not found"}}), 404

    return jsonify({
        "data": {
            "linkId": link_id,
            "status": "healthy",
            "score": 100,
            "baselineRslDbm": row["baseline_rsl_dbm"],
            "lastSeenAt": datetime.now(timezone.utc).isoformat()
        }
    })
