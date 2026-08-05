/**
 * Formats a 0-1 probability as a percentage. Values under 1% round to
 * "0.0%" with a single decimal place, which reads as broken/zero rather
 * than "small but real" (e.g. this model's baseline admission rate is
 * ~0.025%) -- so small values get more decimal places instead.
 */
export function formatPercentage(value) {
  const percentage = value * 100

  if (percentage > 0 && percentage < 0.1) {
    return `${percentage.toFixed(3)}%`
  }

  return `${percentage.toFixed(1)}%`
}
