export async function planTripApi(formData) {
  const baseUrl = import.meta.env.VITE_API_URL || ''
  const endpoint = `${baseUrl.replace(/\/+$/, '')}/api/plan`
  const r = await fetch(endpoint, {
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
