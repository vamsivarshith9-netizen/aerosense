/**
 * app.jsx — AeroSense application root.
 *
 * Responsibilities:
 *  - All React state declarations
 *  - Computed / memoised derived values
 *  - Side-effect hooks (clock, playback timer, map init, map layers, chart)
 *  - API polling and backend forecast request
 *  - Rendering: composes extracted components, passes props down
 *
 * UI sections live in src/components/ — this file only orchestrates them.
 * Data globals (window.DELHI_BBOX, window.CPCB_STATIONS, etc.) are loaded
 * before this script via plain <script> tags in index.html.
 */

const { useState, useEffect, useRef, useMemo } = React;

function AeroSenseApp() {
  // ── Static reference data from delhiData.js ───────────────────────────────
  const stations    = window.CPCB_STATIONS;

  // ── Navigation ────────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState('weather');

  // ── Settings ──────────────────────────────────────────────────────────────
  const [tempUnit, setTempUnit] = useState('C');

  // ── Timeline scrubber ─────────────────────────────────────────────────────
  const [selectedHour, setSelectedHour] = useState(0);
  const [isPlaying,    setIsPlaying]    = useState(false);
  const [playSpeed,    setPlaySpeed]    = useState(1);

  // ── Model selection ───────────────────────────────────────────────────────
  const activeModel = 'modelB';

  // ── Station / CML selection ────────────────────────────────────────────────
  const defaultStationId = stations.find(
    s => s.id.includes('gnoida') || s.name.includes('Greater Noida')
  )?.id || stations[0].id;

  const [selectedStationId, setSelectedStationId] = useState(defaultStationId);
  const [inspectorType,     setInspectorType]     = useState('station');

  // ── Search ────────────────────────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState('');

  // ── Map layer toggles ─────────────────────────────────────────────────────
  const [weatherFieldMode, setWeatherFieldMode] = useState('aqi');
  const [layers, setLayers] = useState({
    field: true, stations: true,
  });

  // ── Real-time clock ───────────────────────────────────────────────────────
  const [currentTimeStr, setCurrentTimeStr] = useState(
    new Date().toLocaleTimeString('en-US', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    })
  );

  // ── Backend API state ─────────────────────────────────────────────────────
  const [apiState, setApiState] = useState({
    status: 'connecting', observations: [], alerts: [],
  });
  const [backendForecast, setBackendForecast] = useState(null);
  const forecastPoints = backendForecast?.forecast || [];
  const weather72h = forecastPoints;

  // ── DOM / library refs ────────────────────────────────────────────────────
  const mapRef              = useRef(null);
  const mapInstanceRef      = useRef(null);
  const heatLayerRef        = useRef(null);
  const stationLayerGroupRef = useRef(null);
  const timerRef            = useRef(null);
  const chartCanvasRef      = useRef(null);
  const chartInstanceRef    = useRef(null);

  // ── Current weather snapshot ──────────────────────────────────────────────
  const liveWeatherObs = useMemo(() =>
    apiState.observations.find(o => o.source === 'weather' && o.deviceId === selectedStationId),
    [apiState.observations, selectedStationId]
  );

  const currentWx = useMemo(() => {
    if (!liveWeatherObs) return {};
    return {
      ...liveWeatherObs,
      temp: liveWeatherObs.temperatureC ?? liveWeatherObs.temp,
      apparentTemp: liveWeatherObs.apparentTemperatureC,
      relativeHumidity: liveWeatherObs.humidityPct ?? liveWeatherObs.relativeHumidity,
      windSpeed: liveWeatherObs.windSpeedMs ?? liveWeatherObs.windSpeed,
      windDir: liveWeatherObs.windDirectionDeg ?? liveWeatherObs.windDir,
      dewPoint: liveWeatherObs.dewPointC,
      sunrise: liveWeatherObs.sunrise,
      sunset: liveWeatherObs.sunset,
      weatherCode: liveWeatherObs.weatherCode,
      timestamp: liveWeatherObs.observedAt ?? liveWeatherObs.timestamp,
    };
  }, [liveWeatherObs]);

  // ── Refresh API telemetry periodically ────────────────────────────────────
  const [telemetryTick, setTelemetryTick] = useState(0);

  useEffect(() => {
    let active = true;
    const refresh = async () => {
      try {
        const [health, aq, weather, cml, alerts] = await Promise.all([
          window.AEROSENSE_API.health(),
          window.AEROSENSE_API.latest('aq_station'),
          window.AEROSENSE_API.latest('weather'),
          window.AEROSENSE_API.latest('cml'),
          window.AEROSENSE_API.alerts(),
        ]);
        if (active) {
          setApiState({
            status: health.status === 'ok' ? 'live' : 'degraded',
            observations: [
              ...(aq.data      || []),
              ...(weather.data || []),
              ...(cml.data     || []),
            ],
            alerts: alerts.data || [],
          });
          setTelemetryTick(t => t + 1);
        }
      } catch {
        if (active) setApiState(prev => ({ ...prev, status: 'offline' }));
      }
    };
    refresh();
    const poll = setInterval(refresh, 60000);
    return () => { active = false; clearInterval(poll); };
  }, []);

  // Live PM2.5 readings indexed by station ID (from backend, if connected)
  const livePm25ByStation = useMemo(() =>
    Object.fromEntries(
      apiState.observations
        .filter(o => o.source === 'aq_station' && Number.isFinite(o.pm25))
        .map(o => [o.deviceId, o.pm25])
    ),
    [apiState.observations]
  );

  // ── Backend ML forecast request ───────────────────────────────────────────
  // Always query trained AI ML engine (CoupledLiveEngine) for selectedStationId.
  useEffect(() => {
    const livePm25 = livePm25ByStation[selectedStationId];
    if (!Number.isFinite(livePm25)) {
      setBackendForecast(null);
      return undefined;
    }

    const weather = apiState.observations.find(
      observation => observation.source === 'weather' && observation.deviceId === selectedStationId
    ) || {};
    const cmlReadings = apiState.observations.filter(
      observation => observation.source === 'cml' && Number.isFinite(observation.rslDbm)
    );
    const features = { pm25: livePm25 };
    if (Number.isFinite(weather.temperatureC)) features.temperatureC = weather.temperatureC;
    if (Number.isFinite(weather.humidityPct)) features.humidityPct = weather.humidityPct;
    if (Number.isFinite(weather.windSpeedMs)) features.windSpeedMs = weather.windSpeedMs;
    const stationObservation = apiState.observations.find(
      observation => observation.source === 'aq_station' && observation.deviceId === selectedStationId
    );
    if (Number.isFinite(stationObservation?.pm10)) features.pm10 = stationObservation.pm10;
    if (cmlReadings.length) {
      features.cmlMeanRslDbm = cmlReadings.reduce((sum, item) => sum + item.rslDbm, 0) / cmlReadings.length;
      features.cmlHealthyLinks = cmlReadings.length;
    }
    let active = true;

    window.AEROSENSE_API.forecast({
      stationId: selectedStationId,
      features,
      horizons: Array.from({ length: 73 }, (_, h) => h),
    })
      .then(result => { if (active) setBackendForecast(result); })
      .catch((err) => {
        console.warn('Backend ML forecast query notice:', err.message);
        if (active) setBackendForecast(null);
      });
    return () => { active = false; };
  }, [selectedStationId, livePm25ByStation, apiState.observations]);

  // ── Helpers ───────────────────────────────────────────────────────────────
  const formatTemp = (celsius) =>
    tempUnit === 'F' ? `${Math.round(celsius * 1.8 + 32)}°F` : `${Math.round(celsius)}°C`;

  // ── Derived / memoised values ─────────────────────────────────────────────
  const currentCmlStates = useMemo(
    () => apiState.observations.filter(observation => observation.source === 'cml'),
    [apiState.observations]
  );

  const selectedStation = useMemo(() => {
    const st   = stations.find(s => s.id === selectedStationId) || stations[0];
    return {
      station: st,
      currentTrajectory: undefined,
      fullTrajectory: [],
    };
  }, [stations, selectedStationId]);

  const selectedCml = currentCmlStates[0];

  const currentStationMetrics = useMemo(() => {
    const liveObsForStation = apiState.observations.find(
      observation => observation.source === 'aq_station' && observation.deviceId === selectedStation.station?.id
    );
    const observedStationReading = selectedHour === 0 ? liveObsForStation : undefined;
    const forecastPoint = forecastPoints.find(point => point.horizonHours === selectedHour);
    const pm25 = selectedHour === 0 ? observedStationReading?.pm25 : forecastPoint?.pm25;
    const preferredAqi = window.FORECAST_ENGINE.getPreferredAQI(
      selectedHour === 0 ? observedStationReading : forecastPoint
    );
    const aqi = preferredAqi.value;
    const aqiStandard = preferredAqi.standard;

    const aqiCategory = window.FORECAST_ENGINE
      ? window.FORECAST_ENGINE.getAQICategory(aqi, aqiStandard)
      : { label: 'N/A', color: '#64748b', stage: 'NORMAL' };

    return {
      pm25,
      pm10: observedStationReading?.pm10,
      no: observedStationReading?.no,
      no2: observedStationReading?.no2,
      so2: observedStationReading?.so2,
      co: observedStationReading?.co,
      o3: observedStationReading?.o3,
      nh3: observedStationReading?.nh3,
      aqi,
      aqiUS: observedStationReading?.aqiUS,
      aqiOpenWeather: observedStationReading?.aqiOpenWeather,
      aqiStandard,
      aqiCategory,
      provider: observedStationReading?.provider,
      dataType: observedStationReading?.dataType,
      aqiMethod: preferredAqi.method,
      observedAt: observedStationReading?.observedAt,
    };
  }, [selectedStation, selectedHour, forecastPoints, apiState.observations]);
  const aqiStandard = currentStationMetrics.aqiStandard;

  const regionalMetrics = useMemo(() => {
    const readings = apiState.observations.filter(
      observation => observation.source === 'aq_station' && Number.isFinite(observation.pm25)
    );
    const avgPM25 = readings.length
      ? readings.reduce((sum, observation) => sum + observation.pm25, 0) / readings.length
      : null;
    const aqi = (avgPM25 !== null && window.FORECAST_ENGINE)
      ? window.FORECAST_ENGINE.calculateAQI(avgPM25, 'IN')
      : null;
    const aqiCategory = (aqi !== null && window.FORECAST_ENGINE)
      ? window.FORECAST_ENGINE.getAQICategory(aqi, 'IN')
      : { label: 'N/A', color: '#64748b' };

    const cmlReadings = apiState.observations.filter(
      observation => observation.source === 'cml' && Number.isFinite(observation.attenuationDb)
    );
    const cmlAttenuations = cmlReadings.map(observation => observation.attenuationDb);
    const avgDeltaRsl = cmlAttenuations.length
      ? +(cmlAttenuations.reduce((sum, attenuation) => sum + attenuation, 0) / cmlAttenuations.length).toFixed(1)
      : null;
    const avgCmlAttenuation = avgDeltaRsl;
    const maxCmlAttenuation = cmlAttenuations.length ? Math.max(...cmlAttenuations) : null;

    return { avgPM25, aqi, aqiCategory, avgCmlAttenuation, maxCmlAttenuation, avgDeltaRsl };
  }, [apiState.observations, currentWx]);

  const rankedStations = useMemo(() =>
    [...stations].map(st => {
      const observation = apiState.observations.find(
        item => item.source === 'aq_station' && item.deviceId === st.id
      );
      const weather = apiState.observations.find(
        item => item.source === 'weather' && item.deviceId === st.id
      );
      const preferredAqi = window.FORECAST_ENGINE.getPreferredAQI(observation);
      const aqi = preferredAqi.value;
      const cat = window.FORECAST_ENGINE.getAQICategory(aqi, preferredAqi.standard);
      return {
        ...st,
        currentPM25: observation?.pm25,
        currentAQI: aqi,
        aqiStandard: preferredAqi.standard,
        cat,
        stationTemp: weather?.temperatureC,
        stationHum: weather?.humidityPct,
      };
    }).sort((a, b) => ((b.currentPM25 ?? -1) - (a.currentPM25 ?? -1))),
    [stations, apiState.observations]
  );

  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase();
    return stations.filter(
      s => s.name.toLowerCase().includes(q) || (s.district && s.district.toLowerCase().includes(q))
    );
  }, [stations, searchQuery]);

  // ── Side effects ──────────────────────────────────────────────────────────

  // Real-time clock
  useEffect(() => {
    const clock = setInterval(() => {
      setCurrentTimeStr(
        new Date().toLocaleTimeString('en-US', {
          timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit',
        })
      );
    }, 1000);
    return () => clearInterval(clock);
  }, []);

  // 72-hour auto-playback timer
  useEffect(() => {
    if (isPlaying) {
      timerRef.current = setInterval(() => {
        setSelectedHour(prev => {
          if (prev >= 72) { setIsPlaying(false); return 72; }
          return prev + 1;
        });
      }, Math.round(1000 / playSpeed));
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [isPlaying, playSpeed]);

  // ── Leaflet map lifecycle & initialization ────────────────────────────────
  const initMap = () => {
    if (!mapRef.current) return;
    if (mapInstanceRef.current) {
      try { mapInstanceRef.current.remove(); } catch (e) {}
      mapInstanceRef.current = null;
    }
    if (mapRef.current._leaflet_id) {
      delete mapRef.current._leaflet_id;
    }

    const map = L.map(mapRef.current, {
      center: [28.474, 77.504], zoom: 11, minZoom: 9, maxZoom: 16,
      zoomControl: false, attributionControl: false,
    });

    const CARTO_API_KEY = 'cb1_3ixp_1_6495ecfd6038be59b57639dc';
    L.tileLayer(`https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png?key=${CARTO_API_KEY}`, {
      maxZoom: 19,
      subdomains: 'abcd',
      attribution: '&copy; CARTO &copy; OpenStreetMap contributors',
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    stationLayerGroupRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    setTimeout(() => map.invalidateSize(), 200);
  };

  useEffect(() => {
    initMap();
    return () => {
      if (mapInstanceRef.current) {
        try { mapInstanceRef.current.remove(); } catch (e) {}
        mapInstanceRef.current = null;
      }
    };
  }, [activeTab]);

  // Invalidate map size on tab switch so Leaflet re-draws tiles
  useEffect(() => {
    if (mapInstanceRef.current) {
      setTimeout(() => mapInstanceRef.current.invalidateSize(), 150);
    }
  }, [activeTab]);

  // Center map helper
  const centerMap = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([28.474, 77.504], 11, { duration: 1.2 });
    }
  };

  // Update AQI / Rain radar heatmap
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !mapRef.current || mapRef.current.clientHeight === 0) return;

    try {
      if (layers.field && typeof L.heatLayer === 'function') {
        let heatPoints, heatGradient;

        if (weatherFieldMode === 'rain') {
          const weather = apiState.observations.find(observation => observation.source === 'weather');
          heatPoints = Number.isFinite(weather?.rain) && Number.isFinite(weather?.latitude) && Number.isFinite(weather?.longitude)
            ? [[weather.latitude, weather.longitude, Math.min(1, weather.rain / 20)]]
            : [];
          heatGradient = { 0.15: '#0ea5e9', 0.35: '#3b82f6', 0.55: '#10b981', 0.75: '#f59e0b', 0.90: '#ef4444' };
        } else {
          heatPoints = apiState.observations
            .filter(observation => observation.source === 'aq_station')
            .flatMap(observation => {
              const station = stations.find(item => item.id === observation.deviceId);
              const preferredAqi = window.FORECAST_ENGINE.getPreferredAQI(observation);
              return station && Number.isFinite(preferredAqi.value)
                ? [[station.lat, station.lon, Math.min(1, preferredAqi.value / 500)]]
                : [];
            });
          heatGradient = aqiStandard === 'US'
            ? { 0.1: '#10b981', 0.2: '#84cc16', 0.3: '#eab308', 0.4: '#f97316', 0.6: '#ef4444', 0.8: '#7f1d1d' }
            : { 0.1: '#10b981', 0.2: '#84cc16', 0.4: '#eab308', 0.6: '#f97316', 0.8: '#ef4444', 1: '#7f1d1d' };
        }

        if (heatLayerRef.current) {
          heatLayerRef.current.setLatLngs(heatPoints);
        } else {
          heatLayerRef.current = L.heatLayer(heatPoints, {
            radius: 36, blur: 26, maxZoom: 14, max: 1.0, minOpacity: 0.22, gradient: heatGradient,
          }).addTo(map);
        }
      } else if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
        heatLayerRef.current = null;
      }
    } catch (err) {
      console.warn('Heatmap canvas update deferred:', err);
    }
  }, [layers.field, weatherFieldMode, stations, activeTab, apiState.observations, telemetryTick, aqiStandard]);

  // Show station markers only when an API reading exists for that station.
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (stationLayerGroupRef.current) stationLayerGroupRef.current.clearLayers();

    if (layers.stations && stationLayerGroupRef.current) {
      stations.forEach(station => {
        const liveObs = apiState.observations.find(
          observation => observation.source === 'aq_station' && observation.deviceId === station.id
        );
        const preferredAqi = window.FORECAST_ENGINE.getPreferredAQI(liveObs);
        if (!Number.isFinite(preferredAqi.value)) return;
        const pm25 = liveObs?.pm25;
        const aqi = preferredAqi.value;
        const cat = window.FORECAST_ENGINE.getAQICategory(aqi, preferredAqi.standard);
        const isSelected = selectedStationId === station.id && inspectorType === 'station';
        const shortCode = station.name.split(' ')[0].substring(0, 4).toUpperCase();

        const badgeIcon = L.divIcon({
          className: 'station-pin-container',
          html: `<div class="station-badge-pill ${isSelected ? 'ring-2 ring-emerald-500 ring-offset-2 ring-offset-white scale-110 shadow-lg' : ''}">
            <span class="station-badge-code">${shortCode}</span>
            <span class="station-badge-val" style="background-color: ${cat.color}; color: #ffffff;">${aqi}</span>
          </div>`,
          iconSize: [68, 26], iconAnchor: [34, 13],
        });

        const marker = L.marker([station.lat, station.lon], { icon: badgeIcon });
        marker.bindTooltip(`
          <div class="font-sans p-1.5 text-slate-800">
            <div class="font-bold text-slate-900 text-xs">${station.name}</div>
            <div class="text-slate-500 text-[10px]">${station.district} &bull; ${station.type}</div>
            <div class="flex items-center gap-2 mt-1.5 pt-1 border-t border-slate-100 text-xs font-semibold">
              <span class="text-emerald-700">${Number.isFinite(pm25) ? `${pm25} µg/m³` : 'Unavailable'} PM2.5</span>
              <span style="color: ${cat.color};">${preferredAqi.standard === 'US' ? 'US EPA' : 'CPCB PM2.5'} AQI ${aqi} (${cat.label})</span>
            </div>
            <div class="text-[10px] text-slate-500 mt-0.5">
              Temp: ${Number.isFinite(currentWx.temp) ? formatTemp(currentWx.temp) : 'N/A'} &bull; RH: ${currentWx.relativeHumidity ?? 'N/A'}% &bull; Wind: ${currentWx.windSpeed ?? 'N/A'} m/s
            </div>
            <div class="text-[9px] text-emerald-700 font-mono mt-1 font-bold">
              ● API observation: ${liveObs.observedAt || liveObs.timestamp || 'timestamp unavailable'}
            </div>
          </div>
        `, { offset: [0, -14] });

        marker.on('click', () => { setSelectedStationId(station.id); setInspectorType('station'); });
        marker.addTo(stationLayerGroupRef.current);
      });
    }
  }, [layers.stations, stations, currentWx, selectedStationId, inspectorType, apiState.observations, telemetryTick]);

  // Chart.js rendering
  useEffect(() => {
    if (!chartCanvasRef.current) return;
    const ctx = chartCanvasRef.current.getContext('2d');
    if (chartInstanceRef.current) chartInstanceRef.current.destroy();

    if (inspectorType === 'cml' && selectedCml) {
      chartInstanceRef.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [selectedCml.observedAt || selectedCml.timestamp || 'Latest API reading'],
          datasets: [
            { label: 'Received Signal Level (RSL in dBm)', data: [selectedCml.rslDbm], borderColor: '#059669', backgroundColor: 'rgba(5,150,105,0.12)', fill: true, tension: 0.35, borderWidth: 2, pointRadius: 2 },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 10, family: 'Inter' } } } }, scales: { x: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 9 } } }, y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 9 } } } } },
      });
    } else {
      const points = forecastPoints.filter((_, i) => i % 3 === 0);

      chartInstanceRef.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: points.map(point => `+${point.horizonHours}h`),
          datasets: [
            { label: 'API PM2.5 forecast (µg/m³)', data: points.map(point => point.pm25), borderColor: '#059669', backgroundColor: 'rgba(5,150,105,0.12)', fill: true, tension: 0.35, borderWidth: 2.2, pointRadius: 2 },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 10, family: 'Inter' } } } }, scales: { x: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 9 } } }, y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 9 } }, title: { display: true, text: 'PM2.5 (µg/m³)', font: { size: 10 } } } } },
      });
    }

    return () => { if (chartInstanceRef.current) { chartInstanceRef.current.destroy(); chartInstanceRef.current = null; } };
  }, [inspectorType, selectedStation, selectedCml, forecastPoints]);

  // ── Navigation helper ─────────────────────────────────────────────────────
  const flyToStation = (stationId) => {
    setSelectedStationId(stationId);
    setInspectorType('station');
    const st = stations.find(s => s.id === stationId);
    if (st && mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([st.lat, st.lon], 13, { duration: 1.2 });
    }
    setSearchQuery('');
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen text-slate-800 font-sans flex flex-col">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <Header
        activeTab={activeTab}          setActiveTab={setActiveTab}
        searchQuery={searchQuery}      setSearchQuery={setSearchQuery}
        searchResults={searchResults}  flyToStation={flyToStation}
        currentTimeStr={currentTimeStr}
        tempUnit={tempUnit}            setTempUnit={setTempUnit}
      />

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <main className="max-w-7xl mx-auto px-4 py-6 flex-1 w-full space-y-6">

        {/* Location and API status */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-2">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black font-heading text-slate-900 tracking-tight">
                {selectedStation.station.name}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold glass-subtle text-slate-700 border border-slate-300/60 flex items-center gap-1.5 shadow-sm">
                <span className="relative flex h-2 w-2">
                  <span className={`relative inline-flex rounded-full h-2 w-2 ${apiState.status === 'live' ? 'bg-emerald-500' : 'bg-slate-400'}`}/>
                </span>
                <span>{apiState.status === 'offline' ? 'API OFFLINE' : `${apiState.observations.length} API OBSERVATIONS`}</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-3 flex-wrap">
              <span>📍 Lat: <strong>{selectedStation.station.lat}° N</strong>, Lon: <strong>{selectedStation.station.lon}° E</strong></span>
              <span>•</span>
              <span>Elevation: <strong>201 m</strong></span>
              <span>•</span>
              <span>Station Type: <strong>{selectedStation.station.type}</strong></span>
              <span>•</span>
              <span>Horizon: <strong>+{selectedHour} Hours</strong></span>
            </p>
          </div>

          <div className="self-start md:self-auto glass-card px-3 py-2 rounded-xl text-xs text-slate-600">
            Forecast model: {backendForecast?.modelVersion || 'No API forecast'}
          </div>
        </div>

        {/* ── Weather & Overview tab ─────────────────────────────────────── */}
        {activeTab === 'weather' && (
          <div className="space-y-6">

           {/* Air Quality Dashboard - Reference Layout */}
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-center">

  {/* Left Side - Air Quality Details */}
  <div className="space-y-5">

    <div className="rounded-2xl bg-indigo-950/80 border border-indigo-400/20 p-6">
      <p className="text-sm text-slate-400">AIR QUALITY INDEX</p>
      <h1 className="text-6xl font-bold text-white mt-2">
        {currentStationMetrics?.aqi ?? "--"}
      </h1>
      <p className="text-sm text-cyan-300 mt-2">
        Current Air Quality
      </p>
    </div>

    <div className="rounded-2xl bg-indigo-950/80 border border-indigo-400/20 p-6">
      <h2 className="text-lg font-semibold text-white mb-3">
        Main Statistics
      </h2>
      <WeatherHeroCard
        currentWx={currentWx}
        formatTemp={formatTemp}
      />
    </div>

    <AQICard
      currentStationMetrics={currentStationMetrics}
    />

  </div>

  {/* Right Side - 3D Earth */}
  <div className="rounded-3xl bg-[#080d27] border border-cyan-400/20 p-4">
    <div className="flex justify-between items-center mb-3">
      <h2 className="text-white font-bold text-sm">
        3D AIR QUALITY GLOBE
      </h2>
      <span className="text-cyan-400 text-xs">
        LIVE VISUALIZATION
      </span>
    </div>

    <EarthGlobe station={selectedStation.station} aqi={currentStationMetrics?.aqi} />
  </div>

</div>

            {/* ── Interactive Radar MAP Prototype Centerpiece ──────────── */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-black font-heading uppercase tracking-wider text-slate-500 flex items-center gap-2">
                    <span>📡 Interactive Radar Map &amp; Atmospheric Field</span>
                    <span className="text-[10px] font-mono text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded-full font-bold">
                      PROTOTYPE RADAR
                    </span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Live 360° radar sweep scanning Delhi-NCR and Greater Noida monitoring stations
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('map')}
                  className="text-xs text-emerald-700 font-bold hover:underline cursor-pointer"
                >
                  Full Radar Screen &rarr;
                </button>
              </div>

              <MapView
                weatherFieldMode={weatherFieldMode}
                setWeatherFieldMode={setWeatherFieldMode}
                layers={layers}
                setLayers={setLayers}
                mapRef={mapRef}
                activeModel={activeModel}
                selectedHour={selectedHour}
                selectedStation={selectedStation}
                currentWx={currentWx}
                formatTemp={formatTemp}
                aqiStandard={currentStationMetrics.aqiStandard}
                centerMap={centerMap}
                observationCount={apiState.observations.length}
              />
            </div>{/* 3D Earth Globe */}
<div className="glass-card rounded-3xl p-5">
  <div className="flex items-center justify-between mb-3">
    <h2 className="text-sm font-bold uppercase tracking-wider">
      3D Atmospheric Earth
    </h2>
    <span className="text-xs text-cyan-400">
      LIVE VISUALIZATION
    </span>
  </div>

  <EarthGlobe station={selectedStation.station} aqi={currentStationMetrics?.aqi} />
  
</div>

            {/* 8-parameter grid */}
            <WeatherParamGrid
              currentWx={currentWx}
              currentStationMetrics={currentStationMetrics}
              formatTemp={formatTemp}
            />

            {/* Hourly forecast scroll */}
            <HourlyForecast
              weather72h={weather72h}
              selectedStation={selectedStation}
              selectedHour={selectedHour}    setSelectedHour={setSelectedHour}
              isPlaying={isPlaying}          setIsPlaying={setIsPlaying}
              playSpeed={playSpeed}          setPlaySpeed={setPlaySpeed}
              activeModel={activeModel}
              formatTemp={formatTemp}
              backendForecast={backendForecast}
            />

            {/* 7-day outlook + health recommendations */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <SevenDayForecast
                weather72h={weather72h}
                selectedStation={selectedStation}
                activeModel={activeModel}
                formatTemp={formatTemp}
                setActiveTab={setActiveTab}
                backendForecast={backendForecast}
              />
              <HealthRecommendations
                aqi={currentStationMetrics.aqi}
                aqiStandard={currentStationMetrics.aqiStandard}
              />
            </div>

            {/* Pollutants grid */}
            <PollutantsGrid
              currentStationMetrics={currentStationMetrics}
              selectedStation={selectedStation}
            />

            {/* Stations table */}
            <StationsTable
              rankedStations={rankedStations}
              selectedStationId={selectedStationId}
              currentWx={currentWx}
              formatTemp={formatTemp}
              flyToStation={flyToStation}
              stations={stations}
            />
          </div>
        )}

        {/* ── Forecast tab ───────────────────────────────────────────────── */}
        {activeTab === 'forecast' && (
          <ForecastTab
            weather72h={weather72h}
            selectedStation={selectedStation}
            activeModel={activeModel}
            formatTemp={formatTemp}
            backendForecast={backendForecast}
          />
        )}

        {/* ── Map tab (Full dedicated view) ──────────────────────────────── */}
        {activeTab === 'map' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-black font-heading text-slate-900">
                  Greater Noida &amp; Delhi-NCR Interactive Atmospheric Radar
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  High-resolution continuous 360° radar telemetry with dispersion modelling &amp; station telemetry
                </p>
              </div>
              <button
                onClick={() => setActiveTab('weather')}
                className="text-xs font-bold text-slate-600 glass-subtle px-3 py-1.5 rounded-xl hover:bg-white cursor-pointer"
              >
                &larr; Back to Overview
              </button>
            </div>

            <MapView
              weatherFieldMode={weatherFieldMode}
              setWeatherFieldMode={setWeatherFieldMode}
              layers={layers}
              setLayers={setLayers}
              mapRef={mapRef}
              activeModel={activeModel}
              selectedHour={selectedHour}
              selectedStation={selectedStation}
              currentWx={currentWx}
              formatTemp={formatTemp}
              centerMap={centerMap}
              observationCount={apiState.observations.length}
            />

            <StationsTable
              rankedStations={rankedStations}
              selectedStationId={selectedStationId}
              currentWx={currentWx}
              formatTemp={formatTemp}
              flyToStation={flyToStation}
              stations={stations}
            />
          </div>
        )}

        {/* ── Pollutants deep-dive tab ───────────────────────────────────── */}
        {activeTab === 'pollutants' && (
          <PollutantsDeepDive
            currentStationMetrics={currentStationMetrics}
            selectedStation={selectedStation}
          />
        )}

      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <Footer />

    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<AeroSenseApp />);
