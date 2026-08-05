import { toChartData } from './GlobalImportanceChart'

/**
 * Plain-language synthesis of the global importance ranking, mirroring
 * explanationSummary.js's per-prediction summary -- so global insights
 * get the same "understandable without ML expertise" treatment
 * (PROJECT_CONTEXT.md §83) as individual predictions do, not just a raw
 * chart of feature names.
 */
export function buildGlobalInsightSummary(topSourceVariables = {}) {
  const [first, second] = toChartData(topSourceVariables)

  if (!first) return 'No global importance data is available yet.'
  if (!second) return `${first.name} is the strongest single driver of the model's predictions overall.`

  return `${first.name} and ${second.name} are the strongest drivers of the model's predictions overall.`
}
