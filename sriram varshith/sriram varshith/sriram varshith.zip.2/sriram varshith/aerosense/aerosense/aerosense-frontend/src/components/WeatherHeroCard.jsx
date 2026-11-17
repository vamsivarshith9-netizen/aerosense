/**
 * WeatherHeroCard.jsx — left hero card showing current temperature & conditions.
 *
 * Props:
 *  currentWx         {Object}  Current weather hour object from weather72h
 *  formatTemp        {Function} (celsius) => formatted string
 */
function WeatherHeroCard({ currentWx, formatTemp }) {
  function getCondition(wx) {
    if (wx?.provider === 'OpenWeatherMap Current Weather') {
      const icons = {
        Thunderstorm: '⛈️',
        Drizzle: '🌦️',
        Rain: '🌧️',
        Snow: '🌨️',
        Mist: '🌫️',
        Smoke: '🌫️',
        Haze: '🌫️',
        Dust: '🌫️',
        Fog: '🌫️',
        Sand: '🌫️',
        Ash: '🌫️',
        Squall: '💨',
        Tornado: '🌪️',
        Clear: '☀️',
        Clouds: '☁️',
      };
      return {
        icon: icons[wx.weatherMain] || '—',
        label: wx.weatherDescription || 'Conditions unavailable',
      };
    }

    const code = wx?.weatherCode;
    if (!Number.isFinite(code)) return { icon: '—', label: 'Conditions unavailable' };
    if (code === 0) return { icon: '☀️', label: 'Clear sky' };
    if (code === 1) return { icon: '🌤️', label: 'Mainly clear' };
    if (code === 2) return { icon: '⛅', label: 'Partly cloudy' };
    if (code === 3) return { icon: '☁️', label: 'Overcast' };
    if (code === 45 || code === 48) return { icon: '🌫️', label: 'Fog' };
    if (code >= 51 && code <= 57) return { icon: '🌦️', label: 'Drizzle' };
    if (code >= 61 && code <= 67) return { icon: '🌧️', label: 'Rain' };
    if (code >= 71 && code <= 77) return { icon: '🌨️', label: 'Snowfall' };
    if (code >= 80 && code <= 82) return { icon: '🌧️', label: 'Rain showers' };
    if (code === 85 || code === 86) return { icon: '🌨️', label: 'Snow showers' };
    if (code >= 95) return { icon: '⛈️', label: 'Thunderstorm' };
    return { icon: '—', label: 'Conditions unavailable' };
  }

  const condition = getCondition(currentWx);

  return (
    <div className="lg:col-span-7 glass-card rounded-3xl p-6 flex flex-col justify-between shadow-sm">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Current Weather
          </span>
          <span className="text-xs text-slate-500 font-mono">
            {currentWx.timestamp ? new Date(currentWx.timestamp).toLocaleString() : 'No API reading'}
          </span>
        </div>

        <div className="flex items-center justify-between gap-4 flex-wrap">
          {/* Big temperature & condition */}
          <div>
            <div className="text-6xl sm:text-7xl font-black font-heading text-slate-900 leading-none tracking-tight">
              {Number.isFinite(currentWx?.temp) ? formatTemp(currentWx.temp) : 'Unavailable'}
            </div>
            <div className="text-base font-bold text-slate-700 mt-2 flex items-center gap-2">
              <span>{condition.label}</span>
              {currentWx.provider && (
                <span className="text-[10px] text-slate-400 font-normal">
                  {currentWx.provider} · {currentWx.dataType}
                </span>
              )}
              {Number.isFinite(currentWx?.apparentTemp) && (
                <>
                  <span className="text-slate-300">•</span>
                  <span className="text-xs text-slate-500 font-normal">
                    Feels like <strong className="text-slate-700">{formatTemp(currentWx.apparentTemp)}</strong>
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Weather emoji graphic */}
          <div className="text-6xl sm:text-7xl drop-shadow-md">
            {condition.icon}
          </div>
        </div>

        {/* Day indicators */}
        <div className="mt-5 pt-4 border-t border-slate-200/60 flex items-center gap-4 text-xs font-semibold text-slate-600 flex-wrap">
          <span className="text-slate-500 font-normal">
            Dew Point: <strong className="text-slate-700">{Number.isFinite(currentWx?.dewPoint) ? formatTemp(currentWx.dewPoint) : 'Unavailable'}</strong>
          </span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500 font-normal">
            Wind: <strong className="text-slate-700">{Number.isFinite(currentWx?.windSpeed) ? `${currentWx.windSpeed} m/s` : 'Unavailable'}</strong>
          </span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500 font-normal">
            Humidity: <strong className="text-sky-700">{Number.isFinite(currentWx?.relativeHumidity) ? `${currentWx.relativeHumidity}%` : 'Unavailable'}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}

window.WeatherHeroCard = WeatherHeroCard;
