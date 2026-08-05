import apiClient from './apiClient'

export function getLiveness() {
  return apiClient.get('/health')
}

export function getModelHealth() {
  return apiClient.get('/health/model')
}

export function getDatabaseHealth() {
  return apiClient.get('/health/db')
}
