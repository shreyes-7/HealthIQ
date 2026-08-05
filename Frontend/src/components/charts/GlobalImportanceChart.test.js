import { describe, expect, it } from 'vitest'
import { toChartData } from './GlobalImportanceChart'

describe('toChartData', () => {
  it('converts a feature-importance object into a sorted array', () => {
    const result = toChartData({ NUMDIS: 1.2, CONSULT: 2.5, TOTDIAG: 0.8 })

    expect(result).toEqual([
      { name: 'CONSULT', value: 2.5 },
      { name: 'NUMDIS', value: 1.2 },
      { name: 'TOTDIAG', value: 0.8 },
    ])
  })

  it('returns an empty array for an empty or missing object', () => {
    expect(toChartData({})).toEqual([])
    expect(toChartData(undefined)).toEqual([])
  })
})
