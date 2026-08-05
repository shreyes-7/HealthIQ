import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { listPredictions } from './historyApi'

vi.mock('./apiClient', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('listPredictions', () => {
  it('defaults limit to 50', () => {
    listPredictions()

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/predictions', { params: { limit: 50 } })
  })

  it('passes through a custom limit', () => {
    listPredictions(10)

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/predictions', { params: { limit: 10 } })
  })
})
