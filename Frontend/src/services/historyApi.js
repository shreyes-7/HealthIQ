import apiClient from './apiClient'

export function listPredictions(limit = 50) {
  return apiClient.get('/api/v1/predictions', { params: { limit } })
}
