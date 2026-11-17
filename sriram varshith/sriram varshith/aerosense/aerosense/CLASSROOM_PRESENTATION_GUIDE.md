# 🎓 AEROSENSE — Classroom Presentation & Project Viva Guide

> **Project Name:** AEROSENSE — Hyper-Local Atmospheric & Air Quality Forecasting Engine  
> **Backend Architecture:** Python Flask REST API (`http://localhost:8000`) with SQLite ACID Persistence  
> **AI ML Architecture:** PyTorch Bi-Directional GRU + Scikit-Learn Multi-Horizon Quantiles ($P_{10}, P_{50}, P_{90}$) + Isolation Forest  
> **Frontend:** Next-Gen Glassmorphic UI with Interactive 360° Radar Sweep, CARTO Positron Basemap, and 72-Hour Diurnal Scrubber (`http://localhost:5173`)  

---

## ⚡ 1. How to Launch the Project for Presentation (1 Click)

### Option A: The 1-Click Presentation Launcher (Recommended)
1. Double-click the file **`start_presentation.bat`** in this folder.
2. It automatically:
   - Starts the **Python Flask API** on port `8000`
   - Starts the **Vite Frontend Dev Server** on port `5173`
   - Opens your default web browser directly to `http://localhost:5173`

### Option B: Manual Two-Terminal Launch
If you want to run it from PowerShell or Command Prompt:

**Terminal 1 — Python Flask Backend:**
```powershell
python run_backend.py
```
*(Runs at `http://localhost:8000` with live database and AI models loaded)*

**Terminal 2 — Frontend:**
```powershell
cd aerosense-frontend
npm run dev
```
*(Runs at `http://localhost:5173`)*

---

## 🎙️ 2. The 5-Minute Presentation Script & Flow

### Step 1: Introduction & Problem Statement (1 Minute)
> *"Respected professors and colleagues, today we present **AeroSense**, a hyper-local atmospheric and particulate forecasting system designed specifically for the Greater Noida and Delhi-NCR airshed.*
>
> *Existing monitoring portals like CPCB only report historical averages with 1-to-2 hour delays and have no predictive foresight. Furthermore, conventional weather models operate at coarse 25–40 km grids that miss street canyons and micro-inversions.*
>
> *AeroSense solves this by coupling continuous ground-station telemetry, meteorological boundary layer physics, and opportunistic Commercial Microwave Links (CML) from cellular towers to forecast PM2.5 and AQI up to 72 hours in advance with probabilistic confidence bounds."*

### Step 2: System Architecture & Backend Highlights (1 Minute)
> *"For our backend, we engineered a modular **Python Flask REST API**. We chose Flask for its clean architecture, high throughput, and seamless integration with our machine learning pipeline:*
> - *It features **SQLite ACID persistence**, eliminating heavy external database dependencies like MongoDB or Redis so it runs reliably anywhere.*
> - *It automatically manages 22 Continuous Ambient Air Quality Monitoring Stations (CAAQMS) and 25 Commercial Microwave Links across Gautam Buddha Nagar and Delhi.*
> - *It serves real-time streaming telemetry with continuous 3-second optical sensor micro-fluctuations.*
> - *It directly drives our deep learning inference engine.*"

### Step 3: Live Application Walkthrough (2 Minutes)
1. **Show the Main Dashboard:**
   - Point out the glowing **`● LIVE CAAQMS TELEMETRY`** badge and the 3-second sync pulse.
   - Point to the bottom-right floating pill: **`API CONNECTED`** (green dot). Click it to reveal the live request log showing real-time REST communication with our Flask server!
2. **Interactive Atmospheric Radar:**
   - Show the rotating 360° radar sweep beam, concentric range rings (10km, 25km, 50km), and Azimuth HUD.
   - Toggle between **AQI Radar** and **Rain Radar**.
3. **Station Selection & Air Quality Donut:**
   - Click on **Knowledge Park III, Greater Noida** (or Pari Chowk, Sector 1).
   - Show the AQI gauge, PM2.5 / PM10 breakdown, and the 8-parameter meteorological grid (Temperature, Humidity, Wind Vector, Dew Point, Boundary Layer Mixing Height).
4. **72-Hour Forecast & Diurnal Scrubber:**
   - Press the **Play** button on the timeline scrubber.
   - Show how PM2.5 fluctuates dynamically between daytime dispersion and nighttime thermal inversions where pollution spikes.
5. **Backend Verification Page:**
   - In a new tab, open `http://localhost:8000/`.
   - Show the Professor the custom **AeroSense Flask API Developer Console**.
   - Click **`GET /api/v1/export/report`** to instantly generate the live executive airshed report with Graded Response Action Plan (GRAP) recommendations!

### Step 4: Conclusion (30 Seconds)
> *"AeroSense demonstrates how modern Python web architecture, coupled atmospheric physics, and neural sequence models can empower urban planners with actionable, proactive environmental intelligence."*

---

## 🧠 3. Professor Q&A Cheat Sheet (Anticipated Viva Questions)

### Q1: Why did you choose Python Flask for the backend instead of Node.js or Django?
**Answer:**
> *"Python is the native language of scientific computing and machine learning. By building the backend with Flask, our web API and our PyTorch/Scikit-Learn ML pipeline run in the exact same Python process space. This avoids inter-process serialization overhead, reduces latency, and removes the need for multiple disparate services. Flask also offers a lightweight, unopinionated structure without Django's unnecessary ORM bloat."*

### Q2: What are Commercial Microwave Links (CML) and how do they detect pollution?
**Answer:**
> *"CMLs are the point-to-point wireless radio hops that connect cellular base stations (telecom towers) across cities, typically operating at 15 to 38 GHz. When heavy particulate matter, fog, or humidity accumulate in the lower atmosphere, the electromagnetic wave experiences signal attenuation (power loss, measured in Received Signal Level - RSL in dBm). Using the ITU-R P.838 atmospheric attenuation model, we invert the signal drop to infer path-averaged particulate and moisture density, giving us virtual sensors between telecom towers without installing expensive monitoring hardware."*

### Q3: How does your AI model forecast 72 hours ahead?
**Answer:**
> *"We use a two-tiered hybrid approach:*
> 1. *A **PyTorch Bi-Directional GRU (Gated Recurrent Unit)** that ingests a 24-hour sliding temporal window (90 engineered features including temporal sinusoidal cycles, wind vectors U and V, ventilation indices, and atmospheric stagnation indices) to predict the multi-step trajectory.*
> 2. *A **Multi-Horizon Quantile Forecaster (`HistGradientBoostingRegressor`)** that outputs $P_{10}$ (optimistic), $P_{50}$ (median), and $P_{90}$ (conservative worst-case) bounds at +1h, +3h, +6h, +12h, +24h, and +72h, enforcing strict mathematical monotonicity ($P_{10} \le P_{50} \le P_{90}$).*"

### Q4: How is data stored and handled if the network goes down?
**Answer:**
> *"The backend uses an embedded SQLite database (`aerosense.db`) with complete ACID transactions and WAL mode. All 22 CAAQMS reference stations, 25 CML topologies, and historical observations are stored locally. If external live feeds drop, the backend automatically transitions to our built-in coupled atmospheric baseline model to ensure zero downtime."*

### Q5: How is AQI computed?
**Answer:**
> *"We strictly follow the official Indian National Air Quality Index (CPCB) sub-index piecewise linear interpolation standard for PM2.5, mapping concentrations to categories from Good (0–50) to Severe (401–500)."*

---

## 📋 4. Key Endpoints Summary

| Endpoint | Method | Presentation Purpose |
|---|---|---|
| `http://localhost:8000/` | `GET` | Developer & Evaluator interactive dashboard |
| `http://localhost:8000/health` | `GET` | Proves backend status, AI model version, and uptime |
| `http://localhost:8000/api/v1/dashboard` | `GET` | Aggregated telemetry, stations, and active alerts |
| `http://localhost:8000/api/v1/stations` | `GET` | Returns all 22 monitoring stations |
| `http://localhost:8000/api/v1/predictions` | `POST` | Core AI forecast generation |
| `http://localhost:8000/api/v1/export/report` | `GET` | Executive airshed report for live demo |
