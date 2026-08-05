import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { submitPrediction } from './predictionApi'

vi.mock('./apiClient', () => ({
  default: { post: vi.fn(), get: vi.fn() },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('submitPrediction', () => {
  it('posts the patient record to /api/v1/predict unmodified', () => {
    const patientRecord = { age: 67, sex: 2 }

    submitPrediction(patientRecord)

    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/predict', patientRecord)
  })
})
