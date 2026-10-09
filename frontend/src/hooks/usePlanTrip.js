import { useState } from 'react'
import { planTripApi } from '../services/planningApi'

export function usePlanTrip() {
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  async function submitPlan(formData, onSuccess) {
    setBusy(true)
    setErr('')
    try {
      const result = await planTripApi(formData)
      setData(result)
      if (onSuccess) onSuccess(result)
    } catch (x) {
      setErr(x.message || 'An error occurred')
    } finally {
      setBusy(false)
    }
  }

  return { data, err, busy, submitPlan }
}
