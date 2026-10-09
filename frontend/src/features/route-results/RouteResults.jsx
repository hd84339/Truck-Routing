import { RouteCard, COLORS, fmt } from './RouteCard'

export function RouteResults({ data, sel, setSel }) {
  if (!data) return null
  const route = data.routes[sel]
  const hasNoTravel = data.routes.every(r => r.summary.no_travel_mi > 0)

  return (
    <>
      <div className="note">
        <b>✅ Recommended: Route {data.recommended + 1}</b><br />
        <small>{data.explanation}</small>
      </div>
      
      {hasNoTravel && (
        <div className="no-travel-warn">
          <h4>⚠️ No Travel Warning</h4>
          <p>Every available route passes through No-Travel conditions based on your load configuration. Delaying departure is strongly advised.</p>
        </div>
      )}

      {[...data.routes].sort((a, b) => a.rank - b.rank).map(r => (
        <RouteCard key={r.id} r={r} sel={sel} recommendedId={data.recommended} setSel={setSel} />
      ))}
      
      <h4>Route {sel + 1} Checkpoints</h4>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Mile</th>
              <th>ETA</th>
              <th>Weather</th>
              <th>Risk Level</th>
            </tr>
          </thead>
          <tbody>
            {route.checkpoints.map(c => (
              <tr key={c.mile} title={c.reason}>
                <td>{c.mile}</td>
                <td>{fmt(c.eta).split(', ')[1] || fmt(c.eta)}</td>
                <td>
                  {c.wind_mph} mph
                  {c.rain_in_hr > 0 && ` · ${c.rain_in_hr}" rain`}
                  {c.snow_in_hr > 0 && ` · ${c.snow_in_hr}" snow`}
                </td>
                <td><span className="badge" style={{ background: COLORS[c.level], margin: 0 }}>{c.label}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
