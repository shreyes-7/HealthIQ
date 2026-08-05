import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getDatabaseHealth, getLiveness, getModelHealth } from './healthApi'

vi.mock('./apiClient', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('health API', () => {
  it('getLiveness calls GET /health', () => {
    getLiveness()
    expect(apiClient.get).toHaveBeenCalledWith('/health')
  })

  it('getModelHealth calls GET /health/model', () => {
    getModelHealth()
    expect(apiClient.get).toHaveBeenCalledWith('/health/model')
  })

  it('getDatabaseHealth calls GET /health/db', () => {
    getDatabaseHealth()
    expect(apiClient.get).toHaveBeenCalledWith('/health/db')
  })
})
