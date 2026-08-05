import axios from 'axios'

/**
 * Normalizes every backend failure (validation error, application error,
 * network failure) into one shape so components never need to branch on
 * where the error came from.
 */
export class ApiError extends Error {
  constructor(message, { statusCode = null, errors = [] } = {}) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.errors = errors
  }
}

// The backend always wraps successful responses as { status: "success", data, ... }
// (Backend.app.schemas.common.SuccessResponse) -- unwrap it once, here, so every
// call site gets the resource directly instead of reaching into `.data.data`.
export function unwrapSuccessResponse(response) {
  return response.data?.data
}

export function normalizeError(error) {
  const backendError = error.response?.data
  if (backendError?.status === 'error') {
    return Promise.reject(
      new ApiError(backendError.message, {
        statusCode: error.response.status,
        errors: backendError.errors ?? [],
      }),
    )
  }

  return Promise.reject(
    new ApiError(error.message || 'Unable to reach the server. Please try again.', { statusCode: null }),
  )
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(unwrapSuccessResponse, normalizeError)

export default apiClient
