import { describe, expect, it } from 'vitest'
import { buildGlobalInsightSummary } from './globalInsightSummary'

describe('buildGlobalInsightSummary', () => {
  it('names the top two drivers, ranked by importance regardless of object key order', () => {
    const summary = buildGlobalInsightSummary({ TOTDIAG: 0.8, NUMDIS: 1.6, CONSULT: 1.2 })

    expect(summary).toBe("NUMDIS and CONSULT are the strongest drivers of the model's predictions overall.")
  })

  it('handles a single driver', () => {
    expect(buildGlobalInsightSummary({ NUMDIS: 1.6 })).toBe(
      "NUMDIS is the strongest single driver of the model's predictions overall.",
    )
  })

  it('handles no data', () => {
    expect(buildGlobalInsightSummary({})).toBe('No global importance data is available yet.')
  })
})
