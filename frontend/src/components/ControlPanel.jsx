import { Ambulance, Zap, Settings, Activity } from "lucide-react";

const EMERGENCY_TYPES = [
  { id: "cardiac", label: "Cardiac",  icon: "❤️",  desc: "Heart attack, cardiac arrest" },
  { id: "trauma",  label: "Trauma",   icon: "🩹",  desc: "Accidents, fractures, bleeding" },
  { id: "neuro",   label: "Neuro",    icon: "🧠",  desc: "Stroke, seizure, head injury" },
  { id: "general", label: "General",  icon: "🏥",  desc: "Burns, infections, other" },
];

function Slider({ label, name, value, min, max, step, onChange, color = "#00D4C8" }) {
  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-xs font-mono font-bold" style={{ color }}>{value}</span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(name, parseFloat(e.target.value))}
        className="w-full h-1 rounded appearance-none cursor-pointer"
        style={{ accentColor: color }}
      />
    </div>
  );
}

export default function ControlPanel({
  emergType, setEmergType,
  params, setParams,
  dispatch, loading,
  startPos, graphInfo,
  status, error,
}) {
  const updateParam = (k, v) => setParams(p => ({ ...p, [k]: v }));

  return (
    <div className="flex flex-col h-full text-sm">

      {/* Header */}
      <div className="px-4 py-4 border-b border-border">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl">🚑</span>
          <div>
            <div className="font-bold text-white text-base leading-tight">LifeLine Navigator</div>
            <div className="text-xs text-gray-500">ACO v5 · Bangalore Road Network</div>
          </div>
        </div>
        {graphInfo && (
          <div className="mt-2 grid grid-cols-2 gap-1">
            {[
              ["Nodes", graphInfo.nodes.toLocaleString()],
              ["Edges", graphInfo.edges.toLocaleString()],
              ["Area",  graphInfo.area_km2 + " km²"],
              ["Source","OpenStreetMap"],
            ].map(([k, v]) => (
              <div key={k} className="bg-up rounded px-2 py-1">
                <div className="text-xs text-gray-500">{k}</div>
                <div className="text-xs font-bold text-cyan">{v}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Status */}
      <div className="px-4 py-2 border-b border-border">
        <div className="flex items-center gap-2">
          <Activity size={12} className={loading ? "text-gold animate-pulse" : "text-cyan"} />
          <span className="text-xs text-gray-400 leading-tight">{status}</span>
        </div>
        {error && (
          <div className="mt-1 text-xs text-red-400 bg-red-900/20 border border-red-800 rounded px-2 py-1">
            {error}
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3">

        {/* Emergency type */}
        <div className="mb-4">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
            Emergency Type
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            {EMERGENCY_TYPES.map(t => (
              <button
                key={t.id}
                onClick={() => setEmergType(t.id)}
                className={`rounded px-2 py-2 text-left transition-all border ${
                  emergType === t.id
                    ? "border-cyan bg-cyan/10 text-white"
                    : "border-border bg-up text-gray-400 hover:border-gray-500"
                }`}
              >
                <div className="text-sm mb-0.5">{t.icon} {t.label}</div>
                <div className="text-xs opacity-60 leading-tight">{t.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Start position indicator */}
        <div className={`mb-4 rounded px-3 py-2 border text-xs ${
          startPos ? "border-cyan/40 bg-cyan/5 text-cyan" : "border-border text-gray-500"
        }`}>
          {startPos
            ? `📍 Start: ${startPos.lat.toFixed(4)}, ${startPos.lon.toFixed(4)}`
            : "📍 Click map to set ambulance start position"}
        </div>

        {/* Dispatch button */}
        <button
          onClick={dispatch}
          disabled={!startPos || loading}
          className={`w-full py-3 rounded font-bold text-sm mb-4 transition-all flex items-center justify-center gap-2 ${
            !startPos || loading
              ? "bg-border text-gray-600 cursor-not-allowed"
              : "bg-red text-white hover:bg-red/90 active:scale-95"
          }`}
        >
          {loading
            ? <><div className="w-3 h-3 border border-white/40 border-t-white rounded-full animate-spin"/><span>Computing route…</span></>
            : <><Zap size={14}/><span>Dispatch Ambulance</span></>
          }
        </button>

        {/* ACO Parameters */}
        <div>
          <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1">
            <Settings size={10}/> ACO Parameters
          </div>
          <Slider label="Iterations"        name="iterations"  value={params.iterations}  min={10}   max={150} step={5}    onChange={updateParam} color="#F5C030" />
          <Slider label="Ants / iteration"  name="ants"        value={params.ants}        min={5}    max={80}  step={5}    onChange={updateParam} color="#F5C030" />
          <Slider label="Alpha α (pheromone)" name="alpha"     value={params.alpha}       min={0.1}  max={5}   step={0.1}  onChange={updateParam} />
          <Slider label="Beta β (heuristic)"  name="beta"      value={params.beta}        min={0.1}  max={5}   step={0.1}  onChange={updateParam} />
          <Slider label="Evaporation ρ"       name="rho"       value={params.rho}         min={0.01} max={0.5} step={0.01} onChange={updateParam} color="#FF3347" />
          <Slider label="Elite ants"          name="elite_ants" value={params.elite_ants} min={0}    max={10}  step={1}    onChange={updateParam} color="#F5C030" />
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-border text-center text-xs text-gray-600">
        DAA Lab 2026 · ECM Dept.
      </div>
    </div>
  );
}
