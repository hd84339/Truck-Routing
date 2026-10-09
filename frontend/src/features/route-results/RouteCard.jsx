export const COLORS = ['#22c55e', '#eab308', '#f97316', '#ef4444', '#a855f7']
export const NAMES = ['Low', 'Moderate', 'High', 'Severe', 'No Travel']
export const ROUTE_COLORS = ['#3b82f6', '#06b6d4', '#d946ef']
export const fmt = (iso) => new Date(iso).toLocaleString([], { weekday: 'short', hour: 'numeric', minute: '2-digit' })

export function RouteCard({ r, sel, recommendedId, setSel }) {
  return (
    <div className={'card' + (sel === r.id ? ' sel' : '')} onClick={() => setSel(r.id)}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <b style={{ color: ROUTE_COLORS[r.id] }}>Route {r.id + 1}</b>
          {r.id === recommendedId && ' ⭐ Recommended'}
        </div>
        <span className="badge" style={{ background: COLORS[r.summary.max_level] }}>
          {NAMES[r.summary.max_level]} Risk
        </span>
      </div>

      <div className="stats">
        <div className="stats-item">
          <span className="stats-val">{r.summary.distance_mi} mi</span>
          <span className="stats-label">Distance</span>
        </div>
        <div className="stats-item">
          <span className="stats-val">{r.summary.duration_h} h</span>
          <span className="stats-label">Time</span>
        </div>
        <div className="stats-item">
          <span className="stats-val">{fmt(r.summary.eta).split(', ')[1] || fmt(r.summary.eta)}</span>
          <span className="stats-label">ETA</span>
        </div>
      </div>

      <div className="risk-summary">
        {r.summary.no_travel_mi > 0 && <span>No-Travel: {r.summary.no_travel_mi} mi</span>}
        {r.summary.severe_mi > 0 && <span>Severe: {r.summary.severe_mi} mi</span>}
        {r.summary.high_mi > 0 && <span>High: {r.summary.high_mi} mi</span>}
        <span>Avg Risk: {r.summary.avg_risk}</span>
      </div>
    </div>
  )
}
