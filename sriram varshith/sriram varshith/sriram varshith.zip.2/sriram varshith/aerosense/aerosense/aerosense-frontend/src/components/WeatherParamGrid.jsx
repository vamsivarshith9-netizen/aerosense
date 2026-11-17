/**
 * WeatherParamGrid.jsx — 8-parameter current conditions grid.
 *
 * Props:
 *  currentWx              {Object}  Current weather hour object
 *  currentStationMetrics  {Object}  { aqi }
 *  formatTemp             {Function}
 */
function WeatherParamGrid({ currentWx, currentStationMetrics, formatTemp }) {
  const providerName = currentWx?.provider || 'Weather API';
  const isHumValid = Number.isFinite(currentWx?.relativeHumidity);
  const isWindValid = Number.isFinite(currentWx?.windSpeed);
  const isPressValid = Number.isFinite(currentWx?.pressure);
  const isVisValid = Number.isFinite(currentWx?.visibility);
  const isUvValid = Number.isFinite(currentWx?.uvIndex);

  const params = [
    {
      icon: '💧', label: 'Humidity',
      value: isHumValid ? `${currentWx.relativeHumidity}%` : 'Unavailable',
      desc: Number.isFinite(currentWx?.dewPoint) ? `Dew Point ${formatTemp(currentWx.dewPoint)}` : 'Dew point N/A',
      barColor: '#0ea5e9',
      pct: isHumValid ? currentWx.relativeHumidity : 0,
    },
    {
      icon: '💨', label: 'Wind Speed',
      value: isWindValid ? `${currentWx.windSpeed} m/s` : 'Unavailable',
      desc: Number.isFinite(currentWx?.windDir) ? `Direction ${currentWx.windDir}°` : 'Wind dir N/A',
      barColor: '#10b981',
      pct: isWindValid ? Math.min((currentWx.windSpeed / 12) * 100, 100) : 0,
    },
    {
      icon: '🧭', label: 'Pressure',
      value: isPressValid ? `${currentWx.pressure} hPa` : 'Unavailable',
      desc: isPressValid ? `${providerName} estimate` : 'No API observation',
      barColor: '#6366f1',
      pct: isPressValid ? Math.min(Math.max(((currentWx.pressure - 980) / 50) * 100, 10), 100) : 0,
    },
    {
      icon: '☀️', label: 'UV Index',
      value: isUvValid ? `${currentWx.uvIndex} of 11` : 'Unavailable',
      desc: isUvValid ? (currentWx.uvIndex > 5 ? 'High UV Exposure' : 'Low / Moderate UV') : 'No API observation',
      barColor: '#f59e0b',
      pct: isUvValid ? Math.min((currentWx.uvIndex / 11) * 100, 100) : 0,
    },
    {
      icon: '👁️', label: 'Visibility',
      value: isVisValid ? `${currentWx.visibility} km` : 'Unavailable',
      desc: isVisValid ? `${providerName} estimate` : 'No API observation',
      barColor: '#8b5cf6',
      pct: isVisValid ? Math.min((currentWx.visibility / 10) * 100, 100) : 0,
    },
    {
      icon: '🌧️', label: 'Precipitation',
      value: Number.isFinite(currentWx?.rain) ? `${currentWx.rain} ${currentWx.rainUnit || 'mm'}` : 'Unavailable',
      desc: Number.isFinite(currentWx?.rain) ? `${providerName} current value` : 'No API observation',
      barColor: '#0284c7',
      pct: Number.isFinite(currentWx?.rain) ? Math.min(currentWx.rain * 15, 100) : 0,
    },
    {
      icon: '🌅', label: 'Sunrise / Sunset',
      value: currentWx.sunrise && currentWx.sunset
        ? `${new Date(currentWx.sunrise).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} / ${new Date(currentWx.sunset).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
        : 'Unavailable',
      desc: currentWx.sunrise && currentWx.sunset ? `${providerName} API` : 'No API observation',
      barColor: '#ec4899',
      pct: 0,
    },
    {
      icon: '🌫️', label: 'Boundary Layer (PBL)',
      value: Number.isFinite(currentWx?.boundaryLayerHeight) ? `${currentWx.boundaryLayerHeight} m` : 'Unavailable',
      desc: Number.isFinite(currentWx?.boundaryLayerHeight) ? (currentWx.isInversionRisk ? 'Inversion trapping' : 'Normal atmospheric mixing') : 'Unavailable',
      barColor: currentWx?.isInversionRisk ? '#ef4444' : '#10b981',
      pct: Number.isFinite(currentWx?.boundaryLayerHeight) ? Math.min((currentWx.boundaryLayerHeight / 2000) * 100, 100) : 0,
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-black font-heading uppercase tracking-wider text-slate-500">
          Greater Noida Current Weather Parameters
        </h2>
        <span className="text-xs text-slate-400">8 API Parameters</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        {params.map(param => (
          <div key={param.label} className="glass-card glass-card-hover rounded-2xl p-4 shadow-sm">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xl">{param.icon}</span>
              <span className="text-[11px] font-semibold text-slate-400">{param.label}</span>
            </div>
            <div className="text-xl sm:text-2xl font-black font-heading text-slate-900 leading-tight">
              {param.value}
            </div>
            <div className="text-[11px] text-slate-500 mt-1 truncate">{param.desc}</div>
            <div className="w-full h-1 bg-slate-200/50 rounded-full mt-2.5 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${param.pct}%`, backgroundColor: param.barColor }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

window.WeatherParamGrid = WeatherParamGrid;
