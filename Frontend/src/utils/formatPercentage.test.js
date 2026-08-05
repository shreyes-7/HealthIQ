import { describe, expect, it } from 'vitest'
import { formatPercentage } from './formatPercentage'

describe('formatPercentage', () => {
  it('formats typical values with one decimal place', () => {
    expect(formatPercentage(0.352)).toBe('35.2%')
    expect(formatPercentage(0.5)).toBe('50.0%')
  })

  it('formats very small non-zero values with more precision instead of rounding to 0.0%', () => {
    expect(formatPercentage(0.00024727871636218493)).toBe('0.025%')
  })

  it('formats a genuine zero as 0.0%', () => {
    expect(formatPercentage(0)).toBe('0.0%')
  })
})
