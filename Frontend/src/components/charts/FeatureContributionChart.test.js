import { describe, expect, it } from 'vitest'
import { selectTopContributions } from './FeatureContributionChart'

describe('selectTopContributions', () => {
  it('ranks by absolute SHAP magnitude regardless of direction', () => {
    const increased = [
      { feature: 'small_increase', shap_value: 0.1 },
      { feature: 'big_increase', shap_value: 3.0 },
    ]
    const decreased = [{ feature: 'medium_decrease', shap_value: -1.5 }]

    const result = selectTopContributions(increased, decreased, 2)

    expect(result.map((entry) => entry.feature)).toEqual(['medium_decrease', 'big_increase'])
  })

  it('sorts the final selection ascending by shap_value for a clean diverging chart', () => {
    const increased = [{ feature: 'a', shap_value: 2 }]
    const decreased = [{ feature: 'b', shap_value: -3 }]

    const result = selectTopContributions(increased, decreased, 5)

    expect(result.map((entry) => entry.feature)).toEqual(['b', 'a'])
  })

  it('caps the result at maxFeatures', () => {
    const increased = Array.from({ length: 10 }, (_, index) => ({ feature: `f${index}`, shap_value: index + 1 }))

    const result = selectTopContributions(increased, [], 3)

    expect(result).toHaveLength(3)
  })

  it('does not mutate the input arrays', () => {
    const increased = [{ feature: 'a', shap_value: 1 }]
    const decreased = [{ feature: 'b', shap_value: -1 }]

    selectTopContributions(increased, decreased)

    expect(increased).toEqual([{ feature: 'a', shap_value: 1 }])
    expect(decreased).toEqual([{ feature: 'b', shap_value: -1 }])
  })

  it('returns an empty array when there are no contributions', () => {
    expect(selectTopContributions([], [])).toEqual([])
  })
})
