import apiClient from './apiClient'

export function getGlobalExplanation(topN = 20) {
  return apiClient.get('/api/v1/explain/global', { params: { top_n: topN } })
}
