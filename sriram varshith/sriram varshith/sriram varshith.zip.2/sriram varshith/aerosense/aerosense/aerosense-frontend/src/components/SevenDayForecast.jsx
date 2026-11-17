/**
 * SevenDayForecast.jsx — sampled PM2.5 forecast points from the backend API.
 */
function SevenDayForecast({ setActiveTab, backendForecast }) {
  const forecast = backendForecast?.forecast || [];
  const points = [0, 24, 48, 72]
    .map(hour => forecast.find(point => point.horizonHours === hour))
    .filter(Boolean);

  return (
    <div className="lg:col-span-7 glass-card rounded-3xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-black font-heading uppercase tracking-wider text-slate-500">
          API Air Quality Forecast
        </h2>
        <span
          className="text-xs text-emerald-700 font-bold cursor-pointer"
          onClick={() => setActiveTab('forecast')}
        >
          View Details &rarr;
        </span>
      </div>
      <p className="text-[10px] text-slate-400 -mt-2 mb-3">
        US EPA AQI estimated from forecast PM2.5
      </p>

      {points.length ? (
        <div className="space-y-2">
          {points.map(point => {
            const preferredAqi = window.FORECAST_ENGINE.getPreferredAQI(point);
            const category = window.FORECAST_ENGINE.getAQICategory(
              preferredAqi.value,
              preferredAqi.standard
            );
            return (
              <div
                key={point.horizonHours}
                className="flex items-center justify-between p-2.5 rounded-2xl glass-subtle text-xs"
              >
                <div>
                  <div className="font-bold text-slate-800">
                    {point.horizonHours === 0 ? 'Now' : `+${point.horizonHours} hours`}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {point.validAt ? new Date(point.validAt).toLocaleString() : 'Time unavailable'}
                  </div>
                </div>
                <span className="font-bold text-slate-700">
                  PM2.5 {Number.isFinite(point.pm25) ? `${point.pm25} µg/m³` : 'Unavailable'}
                </span>
                <span className="font-extrabold" style={{ color: category.color }}>
                  AQI {Number.isFinite(preferredAqi.value) ? preferredAqi.value : 'N/A'}
                </span>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-xs text-slate-500">No forecast data is available from the API.</p>
      )}
    </div>
  );
}

window.SevenDayForecast = SevenDayForecast;
