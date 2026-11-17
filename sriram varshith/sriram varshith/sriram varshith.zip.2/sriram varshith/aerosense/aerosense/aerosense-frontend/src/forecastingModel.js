/**
 * AQI conversion and category helpers for displaying API readings.
 */

(function() {
  function calculateCPCB_AQI(pm25) {
    if (!Number.isFinite(pm25) || pm25 < 0) return null;
    if (pm25 === 0) return 0;
    if (pm25 <= 30.0) return Math.round((50.0 / 30.0) * pm25);
    if (pm25 <= 60.0) return Math.round(50.0 + ((100.0 - 50.0) / (60.0 - 30.0)) * (pm25 - 30.0));
    if (pm25 <= 90.0) return Math.round(100.0 + ((200.0 - 100.0) / (90.0 - 60.0)) * (pm25 - 60.0));
    if (pm25 <= 120.0) return Math.round(200.0 + ((300.0 - 200.0) / (120.0 - 90.0)) * (pm25 - 90.0));
    if (pm25 <= 250.0) return Math.round(300.0 + ((400.0 - 300.0) / (250.0 - 120.0)) * (pm25 - 120.0));
    return Math.min(500, Math.round(400.0 + ((500.0 - 400.0) / (380.0 - 250.0)) * (pm25 - 250.0)));
  }

  function calculateEPA_AQI(pm25) {
    if (!Number.isFinite(pm25) || pm25 < 0) return null;
    if (pm25 === 0) return 0;
    if (pm25 <= 12.0) return Math.round((50 / 12.0) * pm25);
    if (pm25 <= 35.4) return Math.round(51 + ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1));
    if (pm25 <= 55.4) return Math.round(101 + ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5));
    if (pm25 <= 150.4) return Math.round(151 + ((200 - 151) / (150.4 - 55.5)) * (pm25 - 55.5));
    if (pm25 <= 250.4) return Math.round(201 + ((300 - 201) / (250.4 - 150.5)) * (pm25 - 150.5));
    return Math.min(500, Math.round(301 + ((500 - 301) / (500.0 - 250.5)) * (pm25 - 250.5)));
  }

  function calculateAQI(pm25, standard = 'IN') {
    return standard === 'US' ? calculateEPA_AQI(pm25) : calculateCPCB_AQI(pm25);
  }

  function getAQICategory(aqi, standard = 'IN') {
    if (!Number.isFinite(aqi)) {
      return { label: 'N/A', color: '#64748b', bg: 'rgba(100, 116, 139, 0.15)', stage: 'NORMAL' };
    }
    if (standard === 'US') {
      if (aqi <= 50) return { label: 'Good', color: '#22c55e', bg: 'rgba(34, 197, 94, 0.15)', stage: 'NORMAL' };
      if (aqi <= 100) return { label: 'Moderate', color: '#eab308', bg: 'rgba(234, 179, 8, 0.15)', stage: 'NORMAL' };
      if (aqi <= 150) return { label: 'Unhealthy (Sens.)', color: '#f97316', bg: 'rgba(249, 115, 22, 0.15)', stage: 'STAGE I' };
      if (aqi <= 200) return { label: 'Unhealthy', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', stage: 'STAGE II' };
      if (aqi <= 300) return { label: 'Very Unhealthy', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.20)', stage: 'STAGE III' };
      return { label: 'Hazardous', color: '#dc2626', bg: 'rgba(220, 38, 38, 0.25)', stage: 'STAGE IV' };
    }
    if (aqi <= 50) return { label: 'Good', color: '#22c55e', bg: 'rgba(34, 197, 94, 0.15)', stage: 'NORMAL' };
    if (aqi <= 100) return { label: 'Satisfactory', color: '#84cc16', bg: 'rgba(132, 204, 22, 0.15)', stage: 'NORMAL' };
    if (aqi <= 200) return { label: 'Moderate', color: '#eab308', bg: 'rgba(234, 179, 8, 0.15)', stage: 'NORMAL' };
    if (aqi <= 300) return { label: 'Poor', color: '#f97316', bg: 'rgba(249, 115, 22, 0.15)', stage: 'GRAP STAGE I' };
    if (aqi <= 400) return { label: 'Very Poor', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', stage: 'GRAP STAGE II' };
    return { label: 'Severe', color: '#dc2626', bg: 'rgba(220, 38, 38, 0.25)', stage: 'GRAP STAGE III/IV' };
  }

  function getPreferredAQI(observation) {
    if (Number.isFinite(observation?.aqiUS)) {
      return {
        value: observation.aqiUS,
        standard: 'US',
        method: observation?.provider?.includes('Open-Meteo')
          ? 'US AQI from Open-Meteo'
          : 'US AQI from API provider',
      };
    }

    if (Number.isFinite(observation?.pm25)) {
      return {
        value: calculateEPA_AQI(observation.pm25),
        standard: 'US',
        method: 'US EPA AQI estimate from PM2.5',
      };
    }

    return {
      value: null,
      standard: 'US',
      method: 'US AQI is unavailable',
    };
  }

  window.FORECAST_ENGINE = {
    calculateAQI,
    calculateCPCB_AQI,
    calculateEPA_AQI,
    getAQICategory,
    getPreferredAQI,
  };
})();
