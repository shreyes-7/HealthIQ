import { describe, expect, it } from 'vitest'
import { filterPredictionsByRisk, sortPredictions } from './predictionListUtils'

const SAMPLE = [
  { id: '1', created_at: '2026-08-01T10:00:00Z', admission_probability: 0.2, risk_category: 'low' },
  { id: '2', created_at: '2026-08-03T10:00:00Z', admission_probability: 0.9, risk_category: 'high' },
  { id: '3', created_at: '2026-08-02T10:00:00Z', admission_probability: 0.5, risk_category: 'moderate' },
]

describe('sortPredictions', () => {
  it('returns the input unchanged when there is no sort state', () => {
    expect(sortPredictions(SAMPLE, null)).toEqual(SAMPLE)
  })

  it('sorts by timestamp ascending/descending', () => {
    const asc = sortPredictions(SAMPLE, { key: 'created_at', direction: 'asc' })
    expect(asc.map((p) => p.id)).toEqual(['1', '3', '2'])

    const desc = sortPredictions(SAMPLE, { key: 'created_at', direction: 'desc' })
    expect(desc.map((p) => p.id)).toEqual(['2', '3', '1'])
  })

  it('sorts by admission probability', () => {
    const asc = sortPredictions(SAMPLE, { key: 'admission_probability', direction: 'asc' })
    expect(asc.map((p) => p.id)).toEqual(['1', '3', '2'])
  })

  it('sorts by risk category using clinical order (low < moderate < high), not alphabetical', () => {
    const asc = sortPredictions(SAMPLE, { key: 'risk_category', direction: 'asc' })
    expect(asc.map((p) => p.risk_category)).toEqual(['low', 'moderate', 'high'])
  })

  it('does not mutate the input array', () => {
    const copy = [...SAMPLE]
    sortPredictions(SAMPLE, { key: 'admission_probability', direction: 'asc' })
    expect(SAMPLE).toEqual(copy)
  })
})

describe('filterPredictionsByRisk', () => {
  it('returns everything when the filter is "all" or absent', () => {
    expect(filterPredictionsByRisk(SAMPLE, 'all')).toEqual(SAMPLE)
    expect(filterPredictionsByRisk(SAMPLE, undefined)).toEqual(SAMPLE)
  })

  it('filters to only the matching risk category', () => {
    expect(filterPredictionsByRisk(SAMPLE, 'high').map((p) => p.id)).toEqual(['2'])
  })
})
