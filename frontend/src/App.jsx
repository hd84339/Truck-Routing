import { useMemo, useRef, useState, useEffect } from 'react'
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import 'leaflet/dist/leaflet.css'

import { usePlanTrip } from './hooks/usePlanTrip'
import { TripForm } from './features/trip-form/TripForm'
import { RouteResults } from './features/route-results/RouteResults'
import { COLORS, ROUTE_COLORS, fmt } from './features/route-results/RouteCard'

const WEIGHT = [0.05, 0.3, 0.55, 0.85, 1]

function Heat({ points }) {
  const map = useMap(), layer = useRef()
  useEffect(() => {
    layer.current = L.heatLayer([], { radius: 34, blur: 28, maxZoom: 9, max: 1,
      gradient: { 0.2: '#2ecc71', 0.45: '#f1c40f', 0.7: '#e67e22', 1: '#c0392b' } }).addTo(map)
    return () => map.removeLayer(layer.current)
  }, [map])
  useEffect(() => { layer.current?.setLatLngs(points) }, [points])
  return null
}

function Fit({ geoms }) {
  const map = useMap()
  useEffect(() => { if (geoms.length) map.fitBounds(L.latLngBounds(geoms.flat()), { padding: [40, 40] }) }, [geoms, map])
  return null
}

export default function App() {
  const { data, err, busy, submitPlan } = usePlanTrip()
  const [sel, setSel] = useState(0)
  const [hour, setHour] = useState(0)
  const [heat, setHeat] = useState(true)

  const handleSubmit = (formData) => {
    submitPlan(formData, (res) => {
      setSel(res.recommended)
      setHour(0)
    })
  }

  const heatPts = useMemo(() => !data ? [] : data.routes.flatMap(r => r.checkpoints.map(c => [c.lat, c.lng, WEIGHT[c.heat[hour]]])), [data, hour])
  const geoms = useMemo(() => data ? data.routes.map(r => r.geometry) : [], [data])
  const route = data?.routes[sel]

  return (
    <div className="app">
      <div className="side">
        <div className="side-header">
          <h1>🚚 <span>Weather-Aware</span> Truck Routing</h1>
        </div>
        <div className="side-content">
          <TripForm onSubmit={handleSubmit} busy={busy} />
          {err && <div className="err">{err}</div>}
          <RouteResults data={data} sel={sel} setSel={setSel} />
        </div>
      </div>
      <div className="mapwrap">
        <MapContainer className="map" center={[39.5, -98.35]} zoom={4} preferCanvas>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap" />
          <Fit geoms={geoms} />
          {data && data.routes.map(r => (
            <Polyline key={r.id} positions={r.geometry} eventHandlers={{ click: () => setSel(r.id) }}
              pathOptions={{ color: ROUTE_COLORS[r.id], weight: r.id === sel ? 7 : 4, opacity: r.id === sel ? 0.9 : 0.4 }} />
          ))}
          {route && route.checkpoints.map(c => (
            <CircleMarker key={c.mile} center={[c.lat, c.lng]} radius={7}
              pathOptions={{ color: '#fff', weight: 2, fillColor: COLORS[c.level], fillOpacity: 1 }}>
              <Popup>
                <b>Mile {c.mile} — {c.label}</b><br />
                ETA {fmt(c.eta)}<br />
                Wind {c.wind_mph} mph · Rain {c.rain_in_hr} in/hr · Snow {c.snow_in_hr} in/hr<br />
                <small>{c.reason}</small>
              </Popup>
            </CircleMarker>
          ))}
          {data && heat && <Heat points={heatPts} />}
        </MapContainer>
        {data && (
          <div className="slider-panel">
            <div className="slider-header">
              <span>Heatmap Forecast</span>
              <span className="slider-time">
                +{hour}h ({fmt(new Date(new Date(route.checkpoints[0].eta).getTime() + hour * 36e5))})
              </span>
              <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', margin: 0 }}>
                <input type="checkbox" style={{ width: 'auto' }} checked={heat} onChange={e => setHeat(e.target.checked)} /> Show
              </label>
            </div>
            <input type="range" min="0" max="48" value={hour} onChange={e => setHour(+e.target.value)} />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span>Departure</span>
              <span>+24h</span>
              <span>+48h</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
