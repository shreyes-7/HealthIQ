/**
 * Turns the top SHAP contributions into a plain-language sentence, per
 * PROJECT_CONTEXT.md §83: explanations should be understandable without
 * ML expertise, not just a chart of feature names and numbers.
 */
export function buildExplanationSummary({ features_that_increased_risk = [], features_that_decreased_risk = [] }) {
  const topIncrease = features_that_increased_risk[0]
  const topDecrease = features_that_decreased_risk[0]

  if (!topIncrease && !topDecrease) {
    return 'No individual factor stood out as a major driver of this prediction.'
  }

  const clauses = []
  if (topIncrease) {
    clauses.push(`${topIncrease.source_variable} increased the predicted admission risk the most`)
  }
  if (topDecrease) {
    clauses.push(`${topDecrease.source_variable} decreased it the most`)
  }

  return `${clauses.join(', while ')}.`
}
