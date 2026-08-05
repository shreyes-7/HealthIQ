import { useCallback, useEffect, useState } from 'react'

/**
 * One data-fetching pattern for every page: `data`/`loading`/`error`, plus
 * `execute` to (re)trigger the call manually (e.g. on form submit, a retry
 * button, or wired directly as an onClick/onSubmit handler).
 *
 * - `immediate: true` fires the request on mount (and whenever `params` change)
 *   -- for GET-style reads like health checks, global explanation, history.
 * - `immediate: false` (default) only fires when `execute(...)` is called
 *   -- for user-triggered actions like submitting a prediction.
 *
 * `execute` never rejects -- failures are captured in `error` state instead.
 * It's routinely passed directly as an event handler (`onClick={execute}`,
 * `onSubmit={execute}`) across this app; a rejecting promise there would
 * surface as an unhandled promise rejection with no user-visible effect,
 * since nothing downstream awaits or catches it.
 */
export function useApiRequest(apiFunction, { immediate = false, params = [] } = {}) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(immediate)

  const execute = useCallback(
    async (...args) => {
      setLoading(true)
      setError(null)
      try {
        const result = await apiFunction(...args)
        setData(result)
        return result
      } catch (caughtError) {
        setError(caughtError)
        return undefined
      } finally {
        setLoading(false)
      }
    },
    [apiFunction],
  )

  useEffect(() => {
    if (immediate) {
      execute(...params)
    }
    // Only re-run when `immediate` or the params themselves change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate, ...params])

  return { data, error, loading, execute }
}
