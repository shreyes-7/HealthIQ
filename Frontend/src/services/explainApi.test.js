import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getGlobalExplanation } from './explainApi'

vi.mock('./apiClient', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('getGlobalExplanation', () => {
  it('defaults top_n to 20', () => {
    getGlobalExplanation()

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/explain/global', { params: { top_n: 20 } })
  })

  it('passes through a custom top_n', () => {
    getGlobalExplanation(5)

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/explain/global', { params: { top_n: 5 } })
  })
})
