/**
 * ForecastTab.jsx — forecast points returned by the backend API.
 */
function ForecastTab({ backendForecast }) {
  const points = backendForecast?.forecast || [];

  return (
    <div className="space-y-6">
      <div className="glass-card rounded-3xl p-6 shadow-sm">
        <h2 className="text-xl font-black font-heading text-slate-900 mb-1">
          Air Quality Forecast
        </h2>
        <p className="text-xs text-slate-500 mb-6">
          {backendForecast?.modelVersion || 'Waiting for an API forecast'}
        </p>
        <p className="text-[10px] text-slate-400 mb-4">
          US EPA AQI estimated from forecast PM2.5
        </p>

        {points.length ? (
          <div className="space-y-3">
            {points.filter((_, index) => index % 6 === 0 || index === points.length - 1).map(point => {
              const preferredAqi = window.FORECAST_ENGINE.getPreferredAQI(point);
              const category = window.FORECAST_ENGINE.getAQICategory(
                preferredAqi.value,
                preferredAqi.standard
              );
              return (
                <div
                  key={point.horizonHours}
                  className="p-4 rounded-2xl glass-subtle flex items-center justify-between gap-4"
                >
                  <div>
                    <div className="font-bold text-sm text-slate-800">
                      {point.horizonHours === 0 ? 'Now' : `+${point.horizonHours} hours`}
                    </div>
                    <div className="text-xs text-slate-400">
                      {point.validAt ? new Date(point.validAt).toLocaleString() : 'Time unavailable'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-sm text-slate-800">
                      PM2.5: {Number.isFinite(point.pm25) ? `${point.pm25} µg/m³` : 'Unavailable'}
                    </div>
                    <div className="text-xs" style={{ color: category.color }}>
                      AQI: {Number.isFinite(preferredAqi.value) ? preferredAqi.value : 'Unavailable'}{Number.isFinite(preferredAqi.value) ? ` · ${category.label}` : ''}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No forecast data is available from the API.</p>
        )}
      </div>
    </div>
  );
}

window.ForecastTab = ForecastTab;
