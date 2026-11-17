"""
AeroSense Reference & Demonstration Seed Data.
Includes all 22 CAAQMS Greater Noida & Delhi-NCR stations, 25 Commercial Microwave Links,
and baseline observation profiles.
"""
from database import get_db

STATIONS_DATA = [
    {
        "station_id": "ncr_gnoida_kp3",
        "name": "Knowledge Park III, Greater Noida",
        "district": "Gautam Buddha Nagar",
        "station_type": "Institutional & Tech Corridor",
        "latitude": 28.4720,
        "longitude": 77.4890
    },
    {
        "station_id": "ncr_gnoida_pari_chowk",
        "name": "Pari Chowk, Greater Noida",
        "district": "Gautam Buddha Nagar",
        "station_type": "Commercial Transit & Junction",
        "latitude": 28.4650,
        "longitude": 77.5090
    },
    {
        "station_id": "ncr_gnoida_sec1",
        "name": "Sector 1, Greater Noida West",
        "district": "Gautam Buddha Nagar",
        "station_type": "Residential High-Rise Hub",
        "latitude": 28.5830,
        "longitude": 77.4600
    },
    {
        "station_id": "ncr_gnoida_kp5",
        "name": "Knowledge Park V, Greater Noida",
        "district": "Gautam Buddha Nagar",
        "station_type": "Industrial & IT Zone",
        "latitude": 28.5980,
        "longitude": 77.4720
    },
    {
        "station_id": "ncr_noida_sec62",
        "name": "Noida Sector 62, Gautam Buddha Nagar",
        "district": "Gautam Buddha Nagar",
        "station_type": "IT Park / Expressway Hub",
        "latitude": 28.6245,
        "longitude": 77.3578
    },
    {
        "station_id": "ncr_noida_sec1",
        "name": "Noida Sector 1, Industrial",
        "district": "Gautam Buddha Nagar",
        "station_type": "Industrial / Commercial",
        "latitude": 28.5898,
        "longitude": 77.3114
    },
    {
        "station_id": "del_anand_vihar",
        "name": "Anand Vihar, East Delhi",
        "district": "East Delhi",
        "station_type": "Industrial / Inter-State Transit",
        "latitude": 28.6508,
        "longitude": 77.3152
    },
    {
        "station_id": "del_punjabi_bagh",
        "name": "Punjabi Bagh, West Delhi",
        "district": "West Delhi",
        "station_type": "Dense Urban / Ring Road",
        "latitude": 28.6740,
        "longitude": 77.1310
    },
    {
        "station_id": "del_ito",
        "name": "ITO Junction, Central Delhi",
        "district": "Central Delhi",
        "station_type": "Heavy Traffic Intercept",
        "latitude": 28.6310,
        "longitude": 77.2410
    },
    {
        "station_id": "del_rk_puram",
        "name": "R K Puram, South Delhi",
        "district": "South Delhi",
        "station_type": "Residential / Institutional",
        "latitude": 28.5630,
        "longitude": 77.1860
    },
    {
        "station_id": "del_dwarka_sec8",
        "name": "Dwarka Sector 8, South West",
        "district": "South West Delhi",
        "station_type": "Suburban / Airport Corridor",
        "latitude": 28.5710,
        "longitude": 77.0690
    },
    {
        "station_id": "del_bawana",
        "name": "Bawana Industrial Area, North",
        "district": "North Delhi",
        "station_type": "Heavy Industrial Zone",
        "latitude": 28.7762,
        "longitude": 77.0510
    },
    {
        "station_id": "del_jahangirpuri",
        "name": "Jahangirpuri, North Delhi",
        "district": "North Delhi",
        "station_type": "Commercial / Res. Mixed",
        "latitude": 28.7328,
        "longitude": 77.1706
    },
    {
        "station_id": "del_okhla_ph2",
        "name": "Okhla Phase 2, South East",
        "district": "South East Delhi",
        "station_type": "Industrial / Waste-to-Energy",
        "latitude": 28.5307,
        "longitude": 77.2713
    },
    {
        "station_id": "del_wazirpur",
        "name": "Wazirpur Industrial Area",
        "district": "North West Delhi",
        "station_type": "Metals / Finishing Cluster",
        "latitude": 28.6998,
        "longitude": 77.1654
    },
    {
        "station_id": "del_mandir_marg",
        "name": "Mandir Marg, New Delhi",
        "district": "New Delhi",
        "station_type": "Diplomatic / Low Density",
        "latitude": 28.6364,
        "longitude": 77.1973
    },
    {
        "station_id": "del_rohini",
        "name": "Rohini Sector 16, North West",
        "district": "North West Delhi",
        "station_type": "Planned Residential",
        "latitude": 28.7325,
        "longitude": 77.1199
    },
    {
        "station_id": "del_shadipur",
        "name": "Shadipur, West Central",
        "district": "West Delhi",
        "station_type": "Urban Industrial Rail",
        "latitude": 28.6515,
        "longitude": 77.1581
    },
    {
        "station_id": "ncr_gurugram_vikas",
        "name": "Vikas Sadan, Gurugram",
        "district": "Gurugram",
        "station_type": "Urban Center / NH48",
        "latitude": 28.4501,
        "longitude": 77.0264
    },
    {
        "station_id": "ncr_gurugram_teri",
        "name": "TERI Gram, Gwal Pahari",
        "district": "Gurugram",
        "station_type": "Aravalli Ridge Background",
        "latitude": 28.4312,
        "longitude": 77.1511
    },
    {
        "station_id": "ncr_ghaziabad_vasundhara",
        "name": "Vasundhara, Ghaziabad",
        "district": "Ghaziabad",
        "station_type": "Dense Urban / Brick Kiln Path",
        "latitude": 28.6603,
        "longitude": 77.3573
    },
    {
        "station_id": "ncr_faridabad_sec16a",
        "name": "Sector 16A, Faridabad",
        "district": "Faridabad",
        "station_type": "Industrial / Auto Corridor",
        "latitude": 28.4088,
        "longitude": 77.3178
    }
]

CML_LINKS_DATA = [
    {"link_id": "cml_gn_01", "from_tower": "tow_noida_18", "from_lat": 28.6210, "from_lon": 77.3680, "to_tower": "tow_gnoida_sec1", "to_lat": 28.5820, "to_lon": 77.4620, "frequency_ghz": 23.0, "baseline_rsl_dbm": -43.0, "polarization": "H"},
    {"link_id": "cml_gn_02", "from_tower": "tow_gnoida_sec1", "from_lat": 28.5820, "from_lon": 77.4620, "to_tower": "tow_gnoida_kp5", "to_lat": 28.5970, "to_lon": 77.4710, "frequency_ghz": 23.0, "baseline_rsl_dbm": -41.5, "polarization": "V"},
    {"link_id": "cml_gn_03", "from_tower": "tow_noida_17", "from_lat": 28.5670, "from_lon": 77.3210, "to_tower": "tow_gnoida_kp3", "to_lat": 28.4725, "to_lon": 77.4885, "frequency_ghz": 18.0, "baseline_rsl_dbm": -46.2, "polarization": "H"},
    {"link_id": "cml_gn_04", "from_tower": "tow_gnoida_kp3", "from_lat": 28.4725, "from_lon": 77.4885, "to_tower": "tow_gnoida_pari", "to_lat": 28.4660, "to_lon": 77.5080, "frequency_ghz": 38.0, "baseline_rsl_dbm": -39.8, "polarization": "V"},
    {"link_id": "cml_01", "from_tower": "tow_cp_01", "from_lat": 28.6295, "from_lon": 77.2140, "to_tower": "tow_ito_02", "to_lat": 28.6305, "to_lon": 77.2470, "frequency_ghz": 23.0, "baseline_rsl_dbm": -42.5, "polarization": "H"},
    {"link_id": "cml_02", "from_tower": "tow_cp_01", "from_lat": 28.6295, "from_lon": 77.2140, "to_tower": "tow_karol_06", "to_lat": 28.6432, "to_lon": 77.1895, "frequency_ghz": 18.0, "baseline_rsl_dbm": -41.0, "polarization": "V"},
    {"link_id": "cml_03", "from_tower": "tow_karol_06", "from_lat": 28.6432, "from_lon": 77.1895, "to_tower": "tow_pb_05", "to_lat": 28.6690, "to_lon": 77.1270, "frequency_ghz": 18.0, "baseline_rsl_dbm": -44.2, "polarization": "H"},
    {"link_id": "cml_04", "from_tower": "tow_pb_05", "from_lat": 28.6690, "from_lon": 77.1270, "to_tower": "tow_wazir_07", "to_lat": 28.6940, "to_lon": 77.1720, "frequency_ghz": 23.0, "baseline_rsl_dbm": -43.8, "polarization": "V"},
    {"link_id": "cml_05", "from_tower": "tow_wazir_07", "from_lat": 28.6940, "from_lon": 77.1720, "to_tower": "tow_jahan_08", "to_lat": 28.7260, "to_lon": 77.1680, "frequency_ghz": 23.0, "baseline_rsl_dbm": -42.1, "polarization": "H"},
    {"link_id": "cml_06", "from_tower": "tow_wazir_07", "from_lat": 28.6940, "from_lon": 77.1720, "to_tower": "tow_rohini_15", "to_lat": 28.7080, "to_lon": 77.1150, "frequency_ghz": 18.0, "baseline_rsl_dbm": -45.0, "polarization": "H"},
    {"link_id": "cml_07", "from_tower": "tow_rohini_15", "from_lat": 28.7080, "from_lon": 77.1150, "to_tower": "tow_bawana_16", "to_lat": 28.7840, "to_lon": 77.0420, "frequency_ghz": 15.0, "baseline_rsl_dbm": -48.3, "polarization": "V"},
    {"link_id": "cml_08", "from_tower": "tow_ito_02", "from_lat": 28.6305, "from_lon": 77.2470, "to_tower": "tow_anand_09", "to_lat": 28.6480, "to_lon": 77.3100, "frequency_ghz": 15.0, "baseline_rsl_dbm": -49.5, "polarization": "H"},
    {"link_id": "cml_09", "from_tower": "tow_ito_02", "from_lat": 28.6305, "from_lon": 77.2470, "to_tower": "tow_lajpat_12", "to_lat": 28.5700, "to_lon": 77.2390, "frequency_ghz": 18.0, "baseline_rsl_dbm": -45.2, "polarization": "V"},
    {"link_id": "cml_10", "from_tower": "tow_lajpat_12", "from_lat": 28.5700, "from_lon": 77.2390, "to_tower": "tow_okhla_11", "to_lat": 28.5280, "to_lon": 77.2780, "frequency_ghz": 23.0, "baseline_rsl_dbm": -43.0, "polarization": "H"},
    {"link_id": "cml_11", "from_tower": "tow_lajpat_12", "from_lat": 28.5700, "from_lon": 77.2390, "to_tower": "tow_rkp_03", "to_lat": 28.5665, "to_lon": 77.1812, "frequency_ghz": 23.0, "baseline_rsl_dbm": -44.6, "polarization": "V"},
    {"link_id": "cml_12", "from_tower": "tow_rkp_03", "from_lat": 28.5665, "from_lon": 77.1812, "to_tower": "tow_dla_04", "to_lat": 28.5910, "to_lon": 77.1610, "frequency_ghz": 23.0, "baseline_rsl_dbm": -42.0, "polarization": "H"},
    {"link_id": "cml_13", "from_tower": "tow_dla_04", "from_lat": 28.5910, "from_lon": 77.1610, "to_tower": "tow_igi_14", "to_lat": 28.5560, "to_lon": 77.0980, "frequency_ghz": 18.0, "baseline_rsl_dbm": -45.8, "polarization": "V"},
    {"link_id": "cml_14", "from_tower": "tow_igi_14", "from_lat": 28.5560, "from_lon": 77.0980, "to_tower": "tow_dwarka_13", "to_lat": 28.5810, "to_lon": 77.0580, "frequency_ghz": 23.0, "baseline_rsl_dbm": -43.5, "polarization": "H"},
    {"link_id": "cml_15", "from_tower": "tow_dwarka_13", "from_lat": 28.5810, "from_lon": 77.0580, "to_tower": "tow_pb_05", "to_lat": 28.6690, "to_lon": 77.1270, "frequency_ghz": 15.0, "baseline_rsl_dbm": -51.2, "polarization": "V"},
    {"link_id": "cml_16", "from_tower": "tow_anand_09", "from_lat": 28.6480, "from_lon": 77.3100, "to_tower": "tow_ghazi_21", "to_lat": 28.6470, "to_lon": 77.3410, "frequency_ghz": 23.0, "baseline_rsl_dbm": -41.8, "polarization": "H"},
    {"link_id": "cml_17", "from_tower": "tow_ghazi_21", "from_lat": 28.6470, "from_lon": 77.3410, "to_tower": "tow_ghazi_22", "to_lat": 28.6360, "to_lon": 77.3710, "frequency_ghz": 23.0, "baseline_rsl_dbm": -42.4, "polarization": "V"},
    {"link_id": "cml_18", "from_tower": "tow_ghazi_22", "from_lat": 28.6360, "from_lon": 77.3710, "to_tower": "tow_noida_18", "to_lat": 28.6210, "to_lon": 77.3680, "frequency_ghz": 23.0, "baseline_rsl_dbm": -41.2, "polarization": "H"},
    {"link_id": "cml_19", "from_tower": "tow_noida_18", "from_lat": 28.6210, "from_lon": 77.3680, "to_tower": "tow_mayur_10", "to_lat": 28.6050, "to_lon": 77.2980, "frequency_ghz": 18.0, "baseline_rsl_dbm": -46.7, "polarization": "V"},
    {"link_id": "cml_20", "from_tower": "tow_mayur_10", "from_lat": 28.6050, "from_lon": 77.2980, "to_tower": "tow_noida_17", "to_lat": 28.5670, "to_lon": 77.3210, "frequency_ghz": 23.0, "baseline_rsl_dbm": -42.9, "polarization": "H"},
    {"link_id": "cml_21", "from_tower": "tow_noida_17", "from_lat": 28.5670, "from_lon": 77.3210, "to_tower": "tow_okhla_11", "to_lat": 28.5280, "to_lon": 77.2780, "frequency_ghz": 18.0, "baseline_rsl_dbm": -44.0, "polarization": "V"},
    {"link_id": "cml_22", "from_tower": "tow_okhla_11", "from_lat": 28.5280, "from_lon": 77.2780, "to_tower": "tow_badar_24", "to_lat": 28.4990, "to_lon": 77.3020, "frequency_ghz": 23.0, "baseline_rsl_dbm": -42.7, "polarization": "H"},
    {"link_id": "cml_23", "from_tower": "tow_badar_24", "from_lat": 28.4990, "from_lon": 77.3020, "to_tower": "tow_fari_23", "to_lat": 28.3980, "to_lon": 77.3110, "frequency_ghz": 15.0, "baseline_rsl_dbm": -49.8, "polarization": "V"},
    {"link_id": "cml_24", "from_tower": "tow_dla_04", "from_lat": 28.5910, "from_lon": 77.1610, "to_tower": "tow_guru_19", "to_lat": 28.4950, "to_lon": 77.0890, "frequency_ghz": 15.0, "baseline_rsl_dbm": -50.5, "polarization": "H"},
    {"link_id": "cml_25", "from_tower": "tow_guru_19", "from_lat": 28.4950, "from_lon": 77.0890, "to_tower": "tow_guru_20", "to_lat": 28.4720, "to_lon": 77.0650, "frequency_ghz": 38.0, "baseline_rsl_dbm": -40.2, "polarization": "V"}
]

def seed_database_if_needed():
    """Seeds the database if the stations table is empty."""
    conn = get_db()
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM stations").fetchone()[0]

    if count > 0:
        conn.close()
        return False

    print("[Seed] Populating SQLite database with reference stations & CML links...")

    # Insert stations
    for s in STATIONS_DATA:
        cursor.execute("""
        INSERT OR REPLACE INTO stations (station_id, name, district, station_type, latitude, longitude, active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (s["station_id"], s["name"], s["district"], s["station_type"], s["latitude"], s["longitude"]))

    # Insert CML links
    for l in CML_LINKS_DATA:
        cursor.execute("""
        INSERT OR REPLACE INTO cml_links (link_id, from_tower, from_lat, from_lon, to_tower, to_lat, to_lon, frequency_ghz, baseline_rsl_dbm, polarization, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (l["link_id"], l["from_tower"], l["from_lat"], l["from_lon"], l["to_tower"], l["to_lat"], l["to_lon"], l["frequency_ghz"], l["baseline_rsl_dbm"], l["polarization"]))

    conn.commit()
    conn.close()
    print(f"[Seed] Successfully populated {len(STATIONS_DATA)} stations and {len(CML_LINKS_DATA)} CML links.")
    return True
