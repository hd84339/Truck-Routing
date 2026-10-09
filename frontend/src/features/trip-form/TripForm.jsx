import { useState } from 'react'

export function TripForm({ onSubmit, busy }) {
  const [f, setF] = useState({ origin: 'Chicago, IL', destination: 'Denver, CO', departure: '', load_lb: 35000, interval_mi: 25 })
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })

  const submit = (e) => {
    e.preventDefault()
    onSubmit(f)
  }

  return (
    <form onSubmit={submit}>
      <label>Origin</label><input value={f.origin} onChange={set('origin')} required />
      <label>Destination</label><input value={f.destination} onChange={set('destination')} required />
      <label>Departure (blank = in 1 hour)</label><input type="datetime-local" value={f.departure} onChange={set('departure')} />
      <label>Load weight (lb)</label><input type="number" min="0" max="100000" value={f.load_lb} onChange={set('load_lb')} required />
      <label>Weather checkpoint every</label>
      <select value={f.interval_mi} onChange={set('interval_mi')}>
        {[10, 25, 50].map(n => <option key={n} value={n}>{n} miles</option>)}
      </select>
      <button disabled={busy}>{busy ? 'Analyzing routes & weather…' : 'Find safest route'}</button>
    </form>
  )
}
