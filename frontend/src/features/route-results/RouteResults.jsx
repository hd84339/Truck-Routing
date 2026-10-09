import { RouteCard, COLORS, fmt } from './RouteCard'

export function RouteResults({ data, sel, setSel }) {
  if (!data) return null
  const route = data.routes[sel]

  return (
    <>
      <div className="note">✅ Recommended: Route {data.recommended + 1}<br /><small>{data.explanation}</small></div>
      {[...data.routes].sort((a, b) => a.rank - b.rank).map(r => (
        <RouteCard key={r.id} r={r} sel={sel} recommendedId={data.recommended} setSel={setSel} />
      ))}
      <h4>Route {sel + 1} checkpoints</h4>
      <table>
        <tbody>
          {route.checkpoints.map(c => (
            <tr key={c.mile} title={c.reason}>
              <td>{c.mile} mi</td><td>{fmt(c.eta)}</td><td>{c.wind_mph} mph</td>
              <td><span className="badge" style={{ background: COLORS[c.level], margin: 0 }}>{c.label}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
