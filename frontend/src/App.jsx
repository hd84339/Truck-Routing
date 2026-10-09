import { useEffect, useMemo, useRef, useState } from 'react'
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import 'leaflet/dist/leaflet.css'

const COLORS = ['#2e9e5b', '#e0b400', '#e67e22', '#d63031', '#6c2bd9']
const NAMES = ['Low', 'Moderate', 'High', 'Severe', 'No Travel']
const WEIGHT = [0.05, 0.3, 0.55, 0.85, 1]
const ROUTE_COLORS = ['#1d4ed8', '#0891b2', '#9333ea']
const fmt = (iso) => new Date(iso).toLocaleString([], { weekday: 'short', hour: 'numeric', minute: '2-digit' })

function Heat({ points }) {
  const map = useMap(), layer = useRef()
  useEffect(() => {
    layer.current = L.heatLayer([], { radius: 34, blur: 28, maxZoom: 9, max: 1,
      gradient: { 0.2: '#2ecc71', 0.45: '#f1c40f', 0.7: '#e67e22', 1: '#c0392b' } }).addTo(map)
    return () => map.removeLayer(layer.current)
  }, [map])
  useEffect(() => { layer.current?.setLatLngs(points) }, [points])   // cheap update on slider drag
  return null
}

function Fit({ geoms }) {
  const map = useMap()
  useEffect(() => { if (geoms.length) map.fitBounds(L.latLngBounds(geoms.flat()), { padding: [40, 40] }) }, [geoms, map])
  return null
}

export default function App() {
  const [f, setF] = useState({ origin: 'Chicago, IL', destination: 'Denver, CO', departure: '', load_lb: 35000, interval_mi: 25 })
  const [data, setData] = useState(null), [sel, setSel] = useState(0), [err, setErr] = useState(''), [busy, setBusy] = useState(false)
  const [hour, setHour] = useState(0), [heat, setHeat] = useState(true)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })

  async function submit(e) {
    e.preventDefault(); setBusy(true); setErr('')
    try {
      const r = await fetch('/api/plan', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...f, load_lb: +f.load_lb, interval_mi: +f.interval_mi,
          departure: new Date(f.departure || Date.now() + 36e5).toISOString() }) })
      const j = await r.json(); if (!r.ok) throw new Error(j.error)
      setData(j); setSel(j.recommended); setHour(0)
    } catch (x) { setErr(x.message) } finally { setBusy(false) }
  }

  const heatPts = useMemo(() => !data ? [] : data.routes.flatMap(r => r.checkpoints.map(c => [c.lat, c.lng, WEIGHT[c.heat[hour]]])), [data, hour])
  const geoms = useMemo(() => data ? data.routes.map(r => r.geometry) : [], [data])
  const route = data?.routes[sel]

  return (<div className="app">
    <div className="side">
      <h1>🚚 Weather-Aware Truck Routing</h1>
      <form onSubmit={submit}>
        <label>Origin</label><input value={f.origin} onChange={set('origin')} required />
        <label>Destination</label><input value={f.destination} onChange={set('destination')} required />
        <label>Departure (blank = in 1 hour)</label><input type="datetime-local" value={f.departure} onChange={set('departure')} />
        <label>Load weight (lb)</label><input type="number" min="0" max="100000" value={f.load_lb} onChange={set('load_lb')} required />
        <label>Weather checkpoint every</label>
        <select value={f.interval_mi} onChange={set('interval_mi')}>{[10, 25, 50].map(n => <option key={n} value={n}>{n} miles</option>)}</select>
        <button disabled={busy}>{busy ? 'Analyzing routes & weather…' : 'Find safest route'}</button>
      </form>
      {err && <div className="err">{err}</div>}
      {data && <>
        <div className="note">✅ Recommended: Route {data.recommended + 1}<br /><small>{data.explanation}</small></div>
        {[...data.routes].sort((a, b) => a.rank - b.rank).map(r => <div key={r.id} className={'card' + (sel === r.id ? ' sel' : '')} onClick={() => setSel(r.id)}>
          <b style={{ color: ROUTE_COLORS[r.id] }}>Route {r.id + 1}</b>{r.id === data.recommended && ' ⭐'}
          <span className="badge" style={{ background: COLORS[r.summary.max_level] }}>worst: {NAMES[r.summary.max_level]}</span>
          <div>{r.summary.distance_mi} mi · {r.summary.duration_h} h · ETA {fmt(r.summary.eta)}</div>
          <small>Severe {r.summary.severe_mi} mi · No-Travel {r.summary.no_travel_mi} mi · High {r.summary.high_mi} mi · avg risk {r.summary.avg_risk}</small>
        </div>)}
        <h4>Route {sel + 1} checkpoints</h4>
        <table><tbody>{route.checkpoints.map(c => <tr key={c.mile} title={c.reason}>
          <td>{c.mile} mi</td><td>{fmt(c.eta)}</td><td>{c.wind_mph} mph</td>
          <td><span className="badge" style={{ background: COLORS[c.level], margin: 0 }}>{c.label}</span></td></tr>)}</tbody></table>
      </>}
    </div>
    <div className="mapwrap">
      <MapContainer className="map" center={[39.5, -98.35]} zoom={4} preferCanvas>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap" />
        <Fit geoms={geoms} />
        {data && data.routes.map(r => <Polyline key={r.id} positions={r.geometry} eventHandlers={{ click: () => setSel(r.id) }}
          pathOptions={{ color: ROUTE_COLORS[r.id], weight: r.id === sel ? 7 : 4, opacity: r.id === sel ? 0.9 : 0.4 }} />)}
        {route && route.checkpoints.map(c => <CircleMarker key={c.mile} center={[c.lat, c.lng]} radius={7}
          pathOptions={{ color: '#fff', weight: 2, fillColor: COLORS[c.level], fillOpacity: 1 }}>
          <Popup><b>Mile {c.mile} — {c.label}</b><br />ETA {fmt(c.eta)}<br />Wind {c.wind_mph} mph · Rain {c.rain_in_hr} in/hr · Snow {c.snow_in_hr} in/hr<br /><small>{c.reason}</small></Popup>
        </CircleMarker>)}
        {data && heat && <Heat points={heatPts} />}
      </MapContainer>
      {data && <div className="slider">
        <label style={{ margin: 0 }}>Heatmap forecast: +{hour} h after departure ({fmt(new Date(new Date(route.checkpoints[0].eta).getTime() + hour * 36e5))})
          <span style={{ float: 'right' }}><input type="checkbox" style={{ width: 'auto' }} checked={heat} onChange={e => setHeat(e.target.checked)} /> show</span></label>
        <input type="range" min="0" max="48" value={hour} onChange={e => setHour(+e.target.value)} />
      </div>}
    </div>
  </div>)
}
