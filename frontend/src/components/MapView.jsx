import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline,
         CircleMarker, useMapEvents } from "react-leaflet";
import L from "leaflet";

// Fix Leaflet default icon
import iconUrl       from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl     from "leaflet/dist/images/marker-shadow.png";
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl });

// Custom ambulance icon
const ambIcon = L.divIcon({
  html: `<div style="
    width:32px;height:32px;background:#FF3347;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    border:2px solid #fff;font-size:16px;
    box-shadow:0 0 0 4px rgba(255,51,71,0.3)">🚑</div>`,
  iconSize: [32, 32], iconAnchor: [16, 16], popupAnchor: [0, -18],
  className: "",
});

// Hospital icon factory
const hospIcon = (chosen, eligible) => L.divIcon({
  html: `<div style="
    width:28px;height:28px;
    background:${chosen?"#00D4C8":eligible?"#1A3352":"#0F2038"};
    border-radius:50%;display:flex;align-items:center;justify-content:center;
    border:2px solid ${chosen?"#fff":eligible?"#00D4C8":"#1A3352"};
    font-size:14px;">🏥</div>`,
  iconSize:[28,28], iconAnchor:[14,14], popupAnchor:[0,-16], className:"",
});

// Click handler component
function ClickHandler({ onClick }) {
  useMapEvents({ click: (e) => onClick(e.latlng) });
  return null;
}

export default function MapView({ startPos, onMapClick, hospitals, eligibleIds, result }) {
  const BANGALORE = [12.9716, 77.5946];

  const acoPath  = result?.aco_path?.map(c => [c.lat, c.lon])  || [];
  const chosenId = result?.chosen_hospital?.id;

  return (
    <MapContainer
      center={BANGALORE}
      zoom={13}
      style={{ width: "100%", height: "100%" }}
      zoomControl={true}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='© <a href="https://openstreetmap.org">OpenStreetMap</a>'
        maxZoom={19}
      />

      <ClickHandler onClick={onMapClick} />

      {/* Ambulance start marker */}
      {startPos && (
        <Marker position={[startPos.lat, startPos.lon]} icon={ambIcon}>
          <Popup>
            <div className="text-white text-sm font-bold">🚑 Ambulance Position</div>
            <div className="text-gray-400 text-xs">
              {startPos.lat.toFixed(5)}, {startPos.lon.toFixed(5)}
            </div>
          </Popup>
        </Marker>
      )}

      {/* Hospital markers */}
      {hospitals.map(h => {
        const eligible = eligibleIds.includes(h.id);
        const chosen   = h.id === chosenId;
        return (
          <Marker
            key={h.id}
            position={[h.lat, h.lon]}
            icon={hospIcon(chosen, eligible)}
            zIndexOffset={chosen ? 1000 : eligible ? 500 : 0}
          >
            <Popup>
              <div style={{ minWidth: 200, background: "#0A1828", padding: 8, borderRadius: 6 }}>
                <div style={{ color: chosen?"#00D4C8":"#F0F7FF", fontWeight: "bold", marginBottom: 4 }}>
                  {chosen ? "✓ CHOSEN — " : ""}{h.name}
                </div>
                <div style={{ color: "#7A9ABF", fontSize: 12 }}>
                  {h.specialties.join(" · ")}
                </div>
                <div style={{ color: "#7A9ABF", fontSize: 12, marginTop: 4 }}>
                  Capacity: {h.capacity_pct}%  ·  {h.beds} beds  ·  {h.icu_beds} ICU
                </div>
                {result?.all_hospitals?.find(x=>x.id===h.id)?.travel_time_min && (
                  <div style={{ color: "#F5C030", fontSize: 12, marginTop: 4 }}>
                    Travel time: {result.all_hospitals.find(x=>x.id===h.id).travel_time_min} min
                  </div>
                )}
                {!eligible && (
                  <div style={{ color: "#FF3347", fontSize: 11, marginTop: 4 }}>
                    Not eligible for this emergency type
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}

      {/* ACO optimal route */}
      {acoPath.length > 1 && (
        <Polyline
          positions={acoPath}
          pathOptions={{ color: "#FF3347", weight: 4, opacity: 0.9 }}
        />
      )}

      {/* Legend */}
      <div
        className="leaflet-top leaflet-right"
        style={{ pointerEvents: "none" }}
      >
        <div style={{
          margin: 10, background: "rgba(10,24,40,0.92)", border: "1px solid #1A3352",
          borderRadius: 8, padding: "10px 14px", fontSize: 11, color: "#7A9ABF",
          minWidth: 160,
        }}>
          <div style={{ color: "#F0F7FF", fontWeight: "bold", marginBottom: 6, fontSize: 12 }}>
            Legend
          </div>
          {[
            { color: "#FF3347", label: "ACO optimal route" },
            { color: "#00D4C8", label: "Chosen hospital" },
            { color: "#1A3352", label: "Eligible hospital" },
            { color: "#0F2038", label: "Not eligible" },
          ].map(({ color, label }) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: color, flexShrink: 0 }} />
              <span>{label}</span>
            </div>
          ))}
          <div style={{ marginTop: 8, paddingTop: 6, borderTop: "1px solid #1A3352", color: "#334D6E" }}>
            Click map to place ambulance
          </div>
        </div>
      </div>
    </MapContainer>
  );
}
