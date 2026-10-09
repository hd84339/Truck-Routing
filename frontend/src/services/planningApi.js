export async function planTripApi(formData) {
  const r = await fetch('/api/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...formData,
      load_lb: +formData.load_lb,
      interval_mi: +formData.interval_mi,
      departure: new Date(formData.departure || Date.now() + 36e5).toISOString()
    })
  })
  const j = await r.json()
  if (!r.ok) throw new Error(j.error)
  return j
}
