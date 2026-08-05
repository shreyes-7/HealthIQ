/**
 * Pure client-side sort/filter over an already-fetched page of
 * predictions -- no new backend endpoint or API contract change. The
 * backend only supports fetching the N most recent records (`limit`),
 * not true offset-based pagination or server-side sorting/filtering, so
 * this operates entirely on whatever page of data is currently loaded.
 */

const RISK_ORDER = { low: 0, moderate: 1, high: 2 }

export function sortPredictions(predictions, sortState) {
  if (!sortState) return predictions

  const { key, direction } = sortState
  const multiplier = direction === 'asc' ? 1 : -1

  return [...predictions].sort((a, b) => {
    if (key === 'risk_category') {
      return (RISK_ORDER[a.risk_category] - RISK_ORDER[b.risk_category]) * multiplier
    }
    if (key === 'created_at') {
      return (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()) * multiplier
    }
    return (a[key] - b[key]) * multiplier
  })
}

export function filterPredictionsByRisk(predictions, riskFilter) {
  if (!riskFilter || riskFilter === 'all') return predictions
  return predictions.filter((prediction) => prediction.risk_category === riskFilter)
}

/**
 * Aggregates the currently-loaded page of predictions into the summary
 * stats shown above the History table -- computed client-side from data
 * already fetched, not a separate backend call.
 */
export function summarizePredictions(predictions) {
  if (!predictions || predictions.length === 0) {
    return { total: 0, admissionRate: null, highRiskCount: 0, highRiskRate: null }
  }

  const total = predictions.length
  const admissionCount = predictions.filter((prediction) => prediction.predicted_admission).length
  const highRiskCount = predictions.filter((prediction) => prediction.risk_category === 'high').length

  return {
    total,
    admissionRate: admissionCount / total,
    highRiskCount,
    highRiskRate: highRiskCount / total,
  }
}
