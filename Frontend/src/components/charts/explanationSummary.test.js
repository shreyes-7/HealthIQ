import { describe, expect, it } from 'vitest'
import { buildExplanationSummary } from './explanationSummary'

describe('buildExplanationSummary', () => {
  it('mentions both the top increasing and top decreasing factor', () => {
    const summary = buildExplanationSummary({
      features_that_increased_risk: [{ source_variable: 'CONSULT', shap_value: 2.1 }],
      features_that_decreased_risk: [{ source_variable: 'AGE', shap_value: -0.9 }],
    })

    expect(summary).toBe('CONSULT increased the predicted admission risk the most, while AGE decreased it the most.')
  })

  it('handles only an increasing factor', () => {
    const summary = buildExplanationSummary({
      features_that_increased_risk: [{ source_variable: 'CONSULT', shap_value: 2.1 }],
      features_that_decreased_risk: [],
    })

    expect(summary).toBe('CONSULT increased the predicted admission risk the most.')
  })

  it('handles no contributions at all', () => {
    const summary = buildExplanationSummary({ features_that_increased_risk: [], features_that_decreased_risk: [] })

    expect(summary).toBe('No individual factor stood out as a major driver of this prediction.')
  })
})
