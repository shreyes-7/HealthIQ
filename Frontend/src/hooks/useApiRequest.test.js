import { renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { useApiRequest } from './useApiRequest'

describe('useApiRequest', () => {
  it('does not call the API until execute() is invoked when immediate is false', () => {
    const apiFunction = vi.fn().mockResolvedValue({ ok: true })

    const { result } = renderHook(() => useApiRequest(apiFunction))

    expect(apiFunction).not.toHaveBeenCalled()
    expect(result.current.loading).toBe(false)
  })

  it('fires immediately and exposes the resolved data', async () => {
    const apiFunction = vi.fn().mockResolvedValue({ model_name: 'lightgbm' })

    const { result } = renderHook(() => useApiRequest(apiFunction, { immediate: true }))

    expect(result.current.loading).toBe(true)

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.data).toEqual({ model_name: 'lightgbm' })
    expect(result.current.error).toBeNull()
  })

  it('captures a rejected call in `error` without throwing to the caller', async () => {
    const failure = new Error('boom')
    const apiFunction = vi.fn().mockRejectedValue(failure)

    const { result } = renderHook(() => useApiRequest(apiFunction, { immediate: true }))

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.error).toBe(failure)
    expect(result.current.data).toBeNull()
  })

  it('execute() can be called manually and updates state the same way', async () => {
    const apiFunction = vi.fn().mockResolvedValue('done')

    const { result } = renderHook(() => useApiRequest(apiFunction))

    await result.current.execute('some-arg')

    expect(apiFunction).toHaveBeenCalledWith('some-arg')
    await waitFor(() => expect(result.current.data).toBe('done'))
  })
})
