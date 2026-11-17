/**
 * AQICard.jsx — Air Quality Index donut display with health messaging.
 *
 * Props:
 *  currentStationMetrics  {Object}  { aqi, aqiCategory, pm25, aqiStandard }
 */
function AQICard({ currentStationMetrics }) {
  const { aqi, aqiCategory, pm25 } = currentStationMetrics;
  const aqiStandard = currentStationMetrics.aqiStandard || 'IN';
  const color = aqiCategory.color;
  const openWeatherAqi = currentStationMetrics.aqiOpenWeather;
  const openWeatherCategories = ['Unavailable', 'Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'];

  // SVG donut parameters
  const r    = 64;
  const circ = 2 * Math.PI * r;
  const pct  = Math.min(aqi / 500, 1);
  const dash = circ * pct;

  function getHealthMessage(aqi, standard) {
    if (!Number.isFinite(aqi)) return 'Health guidance is unavailable until the API returns an AQI reading.';
    if (standard === 'US') {
      if (aqi > 300) return 'Hazardous air quality. Everyone should avoid outdoor exposure and follow local health guidance.';
      if (aqi > 200) return 'Very unhealthy air quality. Everyone may experience health effects; avoid outdoor activity.';
      if (aqi > 150) return 'Unhealthy air quality. Everyone may experience health effects; sensitive groups should avoid outdoor activity.';
      if (aqi > 100) return 'Unhealthy for sensitive groups. Children, older adults, and people with lung or heart conditions should limit exposure.';
      if (aqi > 50) return 'Moderate air quality. Unusually sensitive people may experience effects.';
      return 'Good air quality poses little or no risk to public health.';
    }
    if (aqi > 400) return 'Severe respiratory emergency! Healthy people experience severe fatigue and respiratory issues; strictly avoid going outdoors.';
    if (aqi > 300) return 'Very Poor air quality! Prolonged exposure causes respiratory illness; avoid outdoor activity and wear an N95 mask.';
    if (aqi > 200) return 'Poor air quality. Breathing discomfort to people with lung/heart disease, children, and elderly on prolonged exposure.';
    if (aqi > 100) return 'Moderate air quality. May cause breathing discomfort to people with lung disease such as asthma and heart issues.';
    if (aqi > 50)  return 'Satisfactory air quality. Minor breathing discomfort to sensitive individuals, acceptable for general public.';
    return 'Good air quality poses minimal health impact and zero risk to public health.';
  }

  return (
    <div className="lg:col-span-5 glass-card rounded-3xl p-6 flex flex-col justify-between shadow-sm">
      <div>
        {/* Header row */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Air Quality Index ({aqiStandard === 'US' ? 'US EPA' : 'CPCB PM2.5 sub-index'})
          </span>
          <span
            className="px-3 py-0.5 rounded-full text-xs font-extrabold"
            style={{
              backgroundColor: color + '22',
              color,
              border: `1px solid ${color}55`,
            }}
          >
            {aqiCategory.label}
          </span>
        </div>

        {/* Donut circle */}
        <div className="flex items-center justify-center my-2">
          <div className="relative w-44 h-44 flex items-center justify-center">
            <svg
              width="176" height="176" viewBox="0 0 176 176"
              style={{ transform: 'rotate(-90deg)', position: 'absolute' }}
            >
              <circle cx="88" cy="88" r={r} fill="none" stroke="rgba(203, 213, 225, 0.4)" strokeWidth="16"/>
              <circle
                cx="88" cy="88" r={r} fill="none"
                stroke={color} strokeWidth="16"
                strokeDasharray={`${dash} ${circ - dash}`}
                strokeLinecap="round"
              />
            </svg>
            <div className="text-center z-10">
              <div className="text-4xl sm:text-5xl font-black font-heading leading-none" style={{ color: Number.isFinite(aqi) ? color : '#64748b' }}>
                {Number.isFinite(aqi) ? aqi : 'N/A'}
              </div>
              <div className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">
                AQI INDEX
              </div>
              <div className="text-xs font-bold mt-0.5 text-slate-700">
                PM2.5: {Number.isFinite(pm25) ? `${pm25} µg/m³` : 'Unavailable'}
              </div>
            </div>
          </div>
        </div>
        <p className="text-[10px] text-slate-400 text-center">
          {currentStationMetrics.aqiMethod || 'CPCB PM2.5 sub-index estimate'}
          {currentStationMetrics.observedAt
            ? ` · Updated ${new Date(currentStationMetrics.observedAt).toLocaleString()}`
            : ''}
        </p>
        {Number.isFinite(openWeatherAqi) && (
          <p className="text-[10px] text-slate-500 text-center">
            OpenWeatherMap AQI: {openWeatherAqi}/5 · {openWeatherCategories[openWeatherAqi] || 'Unavailable'}
          </p>
        )}

        {/* Health message */}
        <div className="text-xs text-slate-600 text-center px-2 mt-1">
          {getHealthMessage(aqi, aqiStandard)}
        </div>
      </div>

      {/* WHO comparison footer */}
      <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-500">
        <span>Prominent Pollutant: <strong className="text-slate-800">PM2.5</strong></span>
        <span className="text-rose-600 font-bold">
          {Number.isFinite(pm25) ? `${(pm25 / 15).toFixed(1)}× WHO Limit` : 'WHO Limit: 15 µg/m³'}
        </span>
      </div>
    </div>
  );
}

window.AQICard = AQICard;
