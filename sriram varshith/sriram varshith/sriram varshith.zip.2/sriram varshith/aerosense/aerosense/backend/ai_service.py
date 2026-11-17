"""
AeroSense AI Inference Service.
Integrates PyTorch GRU Temporal Model, Scikit-Learn Quantile Suite,
and Atmospheric Coupled Feedback for 72-hour air quality intelligence.
"""
import os
import sys
import math
import warnings
from math import exp
from datetime import datetime, timedelta, timezone
from config import MODELS_DIR, PROJECT_ROOT

# Suppress sklearn unpickler warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure 'ai' directory is importable
AI_PATH = os.path.join(PROJECT_ROOT, "ai")
if AI_PATH not in sys.path:
    sys.path.append(AI_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

engine = None
engine_loaded = False
model_version = "baseline-fusion-1.0"

try:
    from inference.live_engine import CoupledLiveEngine
    if os.path.exists(MODELS_DIR):
        print(f"[AI Service] Loading CoupledLiveEngine from {MODELS_DIR}...")
        engine = CoupledLiveEngine(models_dir=MODELS_DIR)
        engine_loaded = True
        model_version = "coupled-gru-quantile-2.0"
        print("[AI Service] Successfully initialized CoupledLiveEngine with PyTorch & Quantile models!")
    else:
        print(f"[AI Service] Notice: Models directory not found at {MODELS_DIR}. Using atmospheric baseline.")
except Exception as exc:
    print(f"[AI Service] Notice: Engine running with built-in atmospheric coupled baseline ({exc})")


def calculate_cpcb_aqi(pm25: float) -> int:
    """Calculates Indian National AQI (CPCB Standard) from PM2.5 concentration."""
    if pm25 <= 0:
        return 0
    if pm25 <= 30:
        return round((50.0 / 30.0) * pm25)
    if pm25 <= 60:
        return round(50.0 + ((100.0 - 50.0) / (60.0 - 30.0)) * (pm25 - 30.0))
    if pm25 <= 90:
        return round(100.0 + ((200.0 - 100.0) / (90.0 - 60.0)) * (pm25 - 60.0))
    if pm25 <= 120:
        return round(200.0 + ((300.0 - 200.0) / (120.0 - 90.0)) * (pm25 - 90.0))
    if pm25 <= 250:
        return round(300.0 + ((400.0 - 300.0) / (250.0 - 120.0)) * (pm25 - 120.0))
    return min(500, round(400.0 + ((500.0 - 400.0) / (380.0 - 250.0)) * (pm25 - 250.0)))


def fallback_atmospheric_forecast(features: dict, hour: int) -> float:
    """Coupled atmospheric physics fallback formula with diurnal cycle and CML damping."""
    pm25 = float(features.get("pm25", 40.0))
    wind_speed = float(features.get("windSpeedMs") or features.get("wind_speed") or 2.5)
    humidity = float(features.get("humidityPct") or features.get("relative_humidity") or 55.0)
    cml_links = int(features.get("cmlHealthyLinks") or 4)

    wind_factor = max(0.85, 1.0 - wind_speed * 0.02)
    humidity_factor = 1.0 + max(0.0, humidity - 60.0) * 0.002
    cml_factor = 1.0 - min(0.05, max(0, cml_links) * 0.008)
    persistence = 0.75 * exp(-hour / 18.0)
    climatology = 38.0 + 5.0 * ((hour % 24) in range(7, 11))
    
    val = (pm25 * persistence + climatology * (1.0 - persistence)) * wind_factor * humidity_factor * cml_factor
    return round(max(5.0, val), 1)


def generate_forecast(station_id: str, features: dict, horizons: list = None) -> dict:
    """
    Generates 0-72 hour forecasts utilizing CoupledLiveEngine or the atmospheric model.
    """
    if horizons is None or len(horizons) == 0:
        horizons = list(range(73))

    issued = datetime.now(timezone.utc)
    horizons_sorted = sorted(set(horizons))
    forecast_results = []

    if engine_loaded and engine is not None:
        try:
            curr_pm25 = float(features.get("pm25", 40.0))
            raw_rec = {
                "time": issued.isoformat(),
                "pm25": curr_pm25,
                "pm10": float(features.get("pm10") or (curr_pm25 * 1.55)),
                "temperature": float(features.get("temperatureC") or features.get("temp") or 29.0),
                "relative_humidity": float(features.get("humidityPct") or features.get("relativeHumidity") or 62.0),
                "wind_speed": float(features.get("windSpeedMs") or features.get("windSpeed") or 2.6),
                "wind_direction": float(features.get("windDirectionDeg") or features.get("windDir") or 315.0),
                "cml_rsl_dbm": float(features.get("cmlMeanRslDbm") or -42.5),
            }
            engine.ingest(raw_rec)
            prediction_state = engine.predict_current_state()

            # Map known AI forecast horizons (0h, 1h, 3h, 6h, 12h, 24h, 72h)
            known_horizons = {0: curr_pm25}
            for k, v in prediction_state.get("multi_horizon_forecasts", {}).items():
                try:
                    h_val = int(k.replace("h", ""))
                    known_horizons[h_val] = float(v["pm25_uncertainty_interval"]["p50_median"])
                except Exception:
                    pass

            sorted_h_keys = sorted(known_horizons.keys())

            def interpolate_ai_pm25(hour: int) -> float:
                if hour in known_horizons:
                    return known_horizons[hour]
                lower_h = sorted_h_keys[0]
                upper_h = sorted_h_keys[-1]
                for hk in sorted_h_keys:
                    if hk <= hour:
                        lower_h = hk
                    if hk >= hour:
                        upper_h = hk
                        break
                if lower_h == upper_h:
                    return known_horizons[lower_h]
                frac = (hour - lower_h) / (upper_h - lower_h)
                val = known_horizons[lower_h] + frac * (known_horizons[upper_h] - known_horizons[lower_h])
                return round(val, 1)

            for h in horizons_sorted:
                pm25_val = interpolate_ai_pm25(h)
                aqi_val = calculate_cpcb_aqi(pm25_val)
                forecast_results.append({
                    "horizonHours": h,
                    "validAt": (issued + timedelta(hours=h)).isoformat(),
                    "pm25": pm25_val,
                    "aqi": aqi_val
                })

            return {
                "stationId": station_id,
                "issuedAt": issued.isoformat(),
                "modelVersion": "coupled-gru-quantile-2.0",
                "disclaimer": "CML/RSL is an atmospheric covariate, not a direct PM2.5 measurement.",
                "forecast": forecast_results,
                "coupledState": prediction_state
            }
        except Exception as err:
            print(f"[AI Service] Live prediction note: {err}. Using smooth atmospheric fusion.")

    # Fallback / baseline path
    for h in horizons_sorted:
        pm25_val = fallback_atmospheric_forecast(features, h)
        aqi_val = calculate_cpcb_aqi(pm25_val)
        forecast_results.append({
            "horizonHours": h,
            "validAt": (issued + timedelta(hours=h)).isoformat(),
            "pm25": pm25_val,
            "aqi": aqi_val
        })

    return {
        "stationId": station_id,
        "issuedAt": issued.isoformat(),
        "modelVersion": "baseline-fusion-1.0",
        "disclaimer": "CML/RSL is an atmospheric covariate, not a direct PM2.5 measurement.",
        "forecast": forecast_results
    }
