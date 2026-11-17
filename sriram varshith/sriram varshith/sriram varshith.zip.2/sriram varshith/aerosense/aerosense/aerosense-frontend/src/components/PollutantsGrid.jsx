/**
 * PollutantsGrid.jsx — API pollutant concentrations with available guideline comparisons.
 *
 * Props:
 *  currentStationMetrics  {Object}  Pollutant readings and provider metadata
 *  selectedStation        {Object}  { station: { name } }
 */
function PollutantsGrid({ currentStationMetrics, selectedStation }) {
  const { pm25, pm10, no, no2, so2, co, o3, nh3, aqiCategory } = currentStationMetrics;

  const getPollutantStatus = (name, val) => {
    if (!Number.isFinite(val)) return { status: 'N/A', color: '#64748b' };
    if (name === 'PM2.5') {
      if (val <= 30) return { status: 'Good', color: '#22c55e' };
      if (val <= 60) return { status: 'Satisfactory', color: '#84cc16' };
      if (val <= 90) return { status: 'Moderate', color: '#eab308' };
      if (val <= 120) return { status: 'Poor', color: '#f97316' };
      if (val <= 250) return { status: 'Very Poor', color: '#ef4444' };
      return { status: 'Severe', color: '#dc2626' };
    }
    if (name === 'PM10') {
      if (val <= 50) return { status: 'Good', color: '#22c55e' };
      if (val <= 100) return { status: 'Satisfactory', color: '#84cc16' };
      if (val <= 250) return { status: 'Moderate', color: '#eab308' };
      if (val <= 350) return { status: 'Poor', color: '#f97316' };
      return { status: 'Very Poor', color: '#ef4444' };
    }
    if (name === 'NO2') {
      if (val <= 40) return { status: 'Good', color: '#22c55e' };
      if (val <= 80) return { status: 'Satisfactory', color: '#84cc16' };
      return { status: 'Moderate', color: '#eab308' };
    }
    if (name === 'SO2') {
      if (val <= 40) return { status: 'Good', color: '#22c55e' };
      if (val <= 80) return { status: 'Satisfactory', color: '#84cc16' };
      return { status: 'Moderate', color: '#eab308' };
    }
    if (name === 'CO') {
      if (val <= 1.0) return { status: 'Good', color: '#22c55e' };
      if (val <= 2.0) return { status: 'Satisfactory', color: '#84cc16' };
      if (val <= 10.0) return { status: 'Moderate', color: '#eab308' };
      return { status: 'Poor', color: '#f97316' };
    }
    if (name === 'Ozone (O3)') {
      if (val <= 50) return { status: 'Good', color: '#22c55e' };
      if (val <= 100) return { status: 'Satisfactory', color: '#84cc16' };
      if (val <= 168) return { status: 'Moderate', color: '#eab308' };
      return { status: 'Poor', color: '#f97316' };
    }
    if (name === 'NO' || name === 'NH3') return { status: 'API data', color: '#0ea5e9' };
    return { status: 'Normal', color: '#22c55e' };
  };

  const p25Status = getPollutantStatus('PM2.5', pm25);
  const p10Status = getPollutantStatus('PM10', pm10);
  const no2Status = getPollutantStatus('NO2', no2);
  const so2Status = getPollutantStatus('SO2', so2);
  const coStatus  = getPollutantStatus('CO', co);
  const o3Status  = getPollutantStatus('Ozone (O3)', o3);

  const pollutants = [
    {
      name: 'PM2.5', value: pm25, unit: 'µg/m³',
      whoLimit: 15, naaqsLimit: 60,
      color: p25Status.color,
      status: p25Status.status,
    },
    {
      name: 'PM10', value: pm10, unit: 'µg/m³',
      whoLimit: 45, naaqsLimit: 100,
      color: p10Status.color, status: p10Status.status,
    },
    {
      name: 'NO2', value: no2, unit: 'µg/m³',
      whoLimit: 25, naaqsLimit: 80,
      color: no2Status.color, status: no2Status.status,
    },
    {
      name: 'SO2', value: so2, unit: 'µg/m³',
      whoLimit: 40, naaqsLimit: 80,
      color: so2Status.color, status: so2Status.status,
    },
    {
      name: 'CO', value: co, unit: 'mg/m³',
      whoLimit: 4, naaqsLimit: 4,
      color: coStatus.color, status: coStatus.status,
    },
    {
      name: 'Ozone (O3)', value: o3, unit: 'µg/m³',
      whoLimit: 100, naaqsLimit: 180,
      color: o3Status.color, status: o3Status.status,
    },
    {
      name: 'NO', value: no, unit: 'µg/m³',
      whoLimit: null, naaqsLimit: null,
      color: getPollutantStatus('NO', no).color, status: getPollutantStatus('NO', no).status,
    },
    {
      name: 'NH3', value: nh3, unit: 'µg/m³',
      whoLimit: null, naaqsLimit: null,
      color: getPollutantStatus('NH3', nh3).color, status: getPollutantStatus('NH3', nh3).status,
    },
  ];

  return (
    <div className="glass-card rounded-3xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-black font-heading text-slate-900">
            Live Air Pollutant Concentrations
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {currentStationMetrics.provider || 'API'} data for {selectedStation.station.name}; guideline comparisons are shown where available
          </p>
        </div>
        <span className="text-xs font-bold text-slate-500">Unit: µg/m³ (CO in mg/m³)</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3.5">
        {pollutants.map(poll => {
          const isAvailable = Number.isFinite(poll.value);
          const hasGuidelines = Number.isFinite(poll.whoLimit) && Number.isFinite(poll.naaqsLimit);
          const displayVal = isAvailable ? poll.value : 'Unavailable';
          const pct = isAvailable && hasGuidelines ? Math.min((poll.value / (poll.naaqsLimit * 1.5)) * 100, 100) : 0;
          return (
            <div key={poll.name} className="p-3.5 rounded-2xl glass-subtle">
              <div className="flex items-center justify-between mb-1">
                <span className="font-extrabold text-xs text-slate-700">{poll.name}</span>
                <span
                  className="text-[10px] font-bold px-1.5 py-0.5 rounded"
                  style={{ backgroundColor: isAvailable ? poll.color + '25' : '#94a3b825', color: isAvailable ? poll.color : '#64748b' }}
                >
                  {isAvailable ? poll.status : 'N/A'}
                </span>
              </div>
              <div className="text-xl sm:text-2xl font-black font-heading text-slate-900 mt-1 truncate">
                {displayVal}
              </div>
              <div className="text-[10px] text-slate-400 mb-2">{isAvailable ? poll.unit : 'No Data'}</div>
              <div className="w-full h-1.5 bg-slate-200/60 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: poll.color }}
                />
              </div>
              <div className="flex justify-between text-[9px] text-slate-400 mt-1.5">
                {hasGuidelines ? (
                  <>
                    <span>WHO: {poll.whoLimit}</span>
                    <span>NAAQS: {poll.naaqsLimit}</span>
                  </>
                ) : <span>No guideline comparison</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

window.PollutantsGrid = PollutantsGrid;
