import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from "recharts";
import { X } from "lucide-react";

function Stat({ label, value, sub, color = "#00D4C8" }) {
  return (
    <div className="flex flex-col items-center bg-up rounded px-3 py-2 min-w-[90px]">
      <span className="text-lg font-bold leading-none" style={{ color }}>{value}</span>
      {sub && <span className="text-xs font-medium mt-0.5" style={{ color: color + "99" }}>{sub}</span>}
      <span className="text-xs text-gray-500 mt-1 text-center leading-tight">{label}</span>
    </div>
  );
}

export default function ResultPanel({ result }) {
  const [open, setOpen] = useState(true);
  if (!open) return (
    <button
      onClick={() => setOpen(true)}
      className="mx-auto mb-2 flex items-center gap-2 bg-surf border border-border rounded px-4 py-1.5 text-xs text-cyan hover:bg-up transition"
    >
      Show results
    </button>
  );

  const convData = result.convergence_data.map((v, i) => ({ iter: i + 1, cost: v }));
  const h = result.chosen_hospital;

  return (
    <div className="bg-surf border-t border-border shadow-2xl" style={{ maxHeight: "42vh", overflowY: "auto" }}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <div className="flex items-center gap-2">
          <span className="text-cyan font-bold text-sm">✓ Route Found</span>
          <span className="text-gray-500 text-xs">→ {h.name}</span>
        </div>
        <button onClick={() => setOpen(false)} className="text-gray-500 hover:text-white p-0.5">
          <X size={14} />
        </button>
      </div>

      <div className="px-4 py-3 flex gap-6 overflow-x-auto">

        {/* Stats row */}
        <div className="flex gap-2 flex-shrink-0">
          <Stat label="ACO ETA"       value={result.aco_travel_time_min + " min"} color="#00D4C8" />
          <Stat label="Dijkstra ETA"  value={result.dijkstra.travel_time_min + " min"} color="#7A9ABF" />
          <Stat label="Time saved"    value={result.time_saved_min + " min"}
                sub={result.time_saved_pct + "% faster"} color="#FF3347" />
          <Stat label="Converged"     value={"iter " + result.converged_at_iter}
                sub={"of " + result.convergence_data.length} color="#F5C030" />
          <Stat label="Ants deployed" value={result.total_ants_deployed.toLocaleString()} color="#F5C030" />
          <Stat label="Road hops"     value={result.aco_hops} color="#00D4C8" />
        </div>

        {/* Hospital info */}
        <div className="border-l border-border pl-4 flex-shrink-0">
          <div className="text-xs font-bold text-cyan mb-1">{h.name}</div>
          <div className="text-xs text-gray-400 space-y-0.5">
            <div>Specialties: {h.specialties.join(", ")}</div>
            <div>Capacity: {h.capacity_pct}%  ·  {h.beds} beds  ·  {h.icu_beds} ICU</div>
          </div>
          {/* All eligible hospitals */}
          <div className="mt-2 flex flex-wrap gap-1">
            {result.all_hospitals.map(ah => (
              <span
                key={ah.id}
                className="text-xs px-1.5 py-0.5 rounded border"
                style={{
                  borderColor: ah.is_chosen ? "#00D4C8" : "#1A3352",
                  color:       ah.is_chosen ? "#00D4C8" : "#7A9ABF",
                  background:  ah.is_chosen ? "rgba(0,212,200,0.08)" : "transparent",
                }}
              >
                {ah.is_chosen ? "✓ " : ""}{ah.name.split("(")[0].trim()}
              </span>
            ))}
          </div>
        </div>

        {/* Convergence chart */}
        <div className="flex-1 min-w-[220px]">
          <div className="text-xs text-gray-500 mb-1">Convergence (best cost per iteration)</div>
          <ResponsiveContainer width="100%" height={90}>
            <LineChart data={convData} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
              <XAxis dataKey="iter" tick={{ fill: "#334D6E", fontSize: 9 }} tickLine={false} />
              <YAxis tick={{ fill: "#334D6E", fontSize: 9 }} tickLine={false} axisLine={false} width={35} />
              <Tooltip
                contentStyle={{ background: "#0A1828", border: "1px solid #1A3352", fontSize: 11 }}
                labelStyle={{ color: "#7A9ABF" }}
                itemStyle={{ color: "#00D4C8" }}
              />
              <ReferenceLine
                x={result.converged_at_iter}
                stroke="#F5C030" strokeDasharray="3 3"
                label={{ value: "converged", position: "top", fill: "#F5C030", fontSize: 9 }}
              />
              <Line
                type="monotone" dataKey="cost" stroke="#FF3347"
                dot={false} strokeWidth={2} isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
