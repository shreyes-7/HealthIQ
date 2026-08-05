import { describe, expect, it } from 'vitest'
import { ApiError, normalizeError, unwrapSuccessResponse } from './apiClient'

describe('unwrapSuccessResponse', () => {
  it('unwraps the backend SuccessResponse envelope to just the resource', () => {
    const axiosResponse = {
      data: {
        status: 'success',
        message: 'Prediction generated successfully.',
        data: { admission_probability: 0.42 },
      },
    }

    expect(unwrapSuccessResponse(axiosResponse)).toEqual({ admission_probability: 0.42 })
  })
})

describe('normalizeError', () => {
  it('normalizes a backend ErrorResponse into an ApiError with field errors', async () => {
    const axiosError = {
      response: {
        status: 422,
        data: {
          status: 'error',
          message: 'Request validation failed.',
          errors: [{ field: 'body.age', message: 'Field required' }],
        },
      },
    }

    await expect(normalizeError(axiosError)).rejects.toMatchObject({
      name: 'ApiError',
      message: 'Request validation failed.',
      statusCode: 422,
      errors: [{ field: 'body.age', message: 'Field required' }],
    })
  })

  it('normalizes a network failure (no response) into an ApiError', async () => {
    const networkError = { message: 'Network Error' }

    await expect(normalizeError(networkError)).rejects.toBeInstanceOf(ApiError)
    await expect(normalizeError(networkError)).rejects.toMatchObject({ statusCode: null })
  })

  it('falls back to a generic message when the network error has none', async () => {
    const networkError = {}

    await expect(normalizeError(networkError)).rejects.toMatchObject({
      message: 'Unable to reach the server. Please try again.',
    })
  })
})
