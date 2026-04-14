import { useState, useEffect, useCallback } from "react";
import MapView       from "./components/MapView";
import ControlPanel  from "./components/ControlPanel";
import ResultPanel   from "./components/ResultPanel";
import { fetchHospitals, fetchGraphInfo, findRoute } from "./api/client";

const DEFAULT_PARAMS = {
  iterations: 40, ants: 20, alpha: 1.0,
  beta: 2.0, rho: 0.15, Q: 100, tau_min: 0.01, tau_max: 5.0, elite_ants: 3,
};

export default function App() {
  // Map state
  const [startPos,  setStartPos]  = useState(null);   // {lat, lon}
  const [hospitals, setHospitals] = useState([]);
  const [emergType, setEmergType] = useState("cardiac");
  const [eligibility, setElig]    = useState({});
  const [graphInfo, setGraphInfo] = useState(null);

  // ACO params
  const [params, setParams] = useState(DEFAULT_PARAMS);

  // Result state
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);
  const [status,  setStatus]  = useState("Click on the map to set ambulance start position");

  // Load hospitals and graph info on mount
  useEffect(() => {
    fetchHospitals()
      .then(d => { setHospitals(d.hospitals); setElig(d.emergency_types); })
      .catch(() => setError("Could not connect to API. Is the backend running?"));
    fetchGraphInfo()
      .then(setGraphInfo)
      .catch(() => {});
  }, []);

  const handleMapClick = useCallback((latlng) => {
    setStartPos({ lat: latlng.lat, lon: latlng.lng });
    setResult(null);
    setStatus(`Start: ${latlng.lat.toFixed(4)}, ${latlng.lng.toFixed(4)} — ready to dispatch`);
  }, []);

  const dispatch = useCallback(async () => {
    if (!startPos) { setError("Click on the map first to set ambulance position."); return; }
    setLoading(true);
    setError(null);
    setResult(null);
    setStatus("Running ACO on real Bangalore road network …");
    try {
      const r = await findRoute({
        start_lat:      startPos.lat,
        start_lon:      startPos.lon,
        emergency_type: emergType,
        aco_params:     params,
      });
      setResult(r);
      setStatus(`Route found → ${r.chosen_hospital.name}  (${r.aco_travel_time_min} min)`);
    } catch (e) {
      const msg = e?.response?.data?.detail || e.message || "Unknown error";
      setError(msg);
      setStatus("Error — see below");
    } finally {
      setLoading(false);
    }
  }, [startPos, emergType, params]);

  const eligibleIds = eligibility[emergType] || [];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-bg text-white">

      {/* ── Left sidebar ── */}
      <aside className="w-80 flex-shrink-0 flex flex-col bg-surf border-r border-border overflow-y-auto z-10">
        <ControlPanel
          emergType={emergType}
          setEmergType={setEmergType}
          params={params}
          setParams={setParams}
          dispatch={dispatch}
          loading={loading}
          startPos={startPos}
          graphInfo={graphInfo}
          status={status}
          error={error}
        />
      </aside>

      {/* ── Main map ── */}
      <main className="flex-1 relative">
        <MapView
          startPos={startPos}
          onMapClick={handleMapClick}
          hospitals={hospitals}
          eligibleIds={eligibleIds}
          result={result}
        />

        {/* Result panel — slides up from bottom when route found */}
        {result && (
          <div className="absolute bottom-0 left-0 right-0 z-[1000]">
            <ResultPanel result={result} />
          </div>
        )}
      </main>
    </div>
  );
}
