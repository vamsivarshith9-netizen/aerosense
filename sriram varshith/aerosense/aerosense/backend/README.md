# AEROSENSE Python Flask Backend API

High-performance, lightweight Python Flask API powering the AEROSENSE Delhi-NCR & Greater Noida atmospheric intelligence and air quality forecasting system.

## 🚀 Key Features

- **Pure Python Flask Backend**: Eliminates external complexity (no MongoDB or Redis required; uses ACID SQLite persistence).
- **Embedded AI ML Engine (`CoupledLiveEngine`)**:
  - **PyTorch Bi-Directional GRU**: Continuous 72-hour sequence trajectory forecasting.
  - **Quantile Regressors (HistGradientBoosting)**: Probabilistic uncertainty bounds ($P_{10}, P_{50}, P_{90}$) across multi-horizons (1h, 3h, 6h, 12h, 24h, 72h).
  - **Isolation Forest**: Real-time pollution anomaly and industrial sensor spike detection.
  - **Explainable AI (XAI)**: Feature causal attribution (traffic, meteorology, boundary layer compression).
- **CML Microwave Sensing Physics**: Integrated telemetry for 25 Commercial Microwave Links connecting telecom towers across Greater Noida, Noida, and Delhi.
- **Continuous 3-Second Live Streaming**: Dynamically fluctuates optical PM2.5/PM10 readings to simulate real CAAQMS telemetry.
- **Interactive Landing Page**: Visit `http://localhost:8000/` in any browser to inspect API status and test endpoints interactively.

---

## 📦 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Flask, Flask-CORS, PyTorch, Scikit-Learn, Joblib, Pandas, NumPy)*

### 2. Start Backend Server
From this directory:
```bash
python app.py
```
Or from the project root:
```bash
python run_backend.py
```

Default Port: `8000` (customizable via `--port <PORT>` or `PORT` environment variable).

### 3. Verify Health
Open in browser or terminal:
```bash
curl http://localhost:8000/health
```

---

## 🌐 API Reference

All responses return standard JSON.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Interactive HTML Developer Dashboard & Endpoint Tester |
| `GET` | `/health` or `/api/v1/health` | Service status, active model version, and DB status |
| `GET` | `/api/v1/dashboard` | Aggregated dashboard data (stations, latest readings, alerts) |
| `GET` | `/api/v1/stations` | All 22 CAAQMS Greater Noida & Delhi-NCR stations |
| `GET` | `/api/v1/stations/<stationId>` | Detailed metadata and recent readings for a specific station |
| `GET` | `/api/v1/weather` | Current meteorological observations (temp, RH, wind, PBLH) |
| `GET` | `/api/v1/observations/latest` | Latest observations (filters: `?source=aq_station`, `weather`, `cml`) |
| `POST` | `/api/v1/predictions` | 72-hour coupled AI forecast ($P_{10}, P_{50}, P_{90}$ quantiles) |
| `GET` | `/api/v1/cml/links` | 25 Commercial Microwave Link topologies and health |
| `GET` | `/api/v1/cml/links/<linkId>/health`| Single CML link operational health |
| `POST` | `/api/v1/telemetry/sync` | Live telemetry synchronization heartbeat |
| `POST` | `/api/v1/ingestion/observations` | Ingest external sensor telemetry batches |
| `GET` | `/api/v1/export/report` | Executive Airshed Summary Report for presentations |

---

## 🧪 Testing

Run automated tests:
```bash
python -c "from app import create_app; client = create_app().test_client(); print(client.get('/health').json)"
```
