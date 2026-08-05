import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const INCREASE_COLOR = 'var(--destructive)'
const DECREASE_COLOR = 'var(--success)'

/**
 * Combines increased/decreased-risk contributions into one diverging bar
 * chart (red = pushed toward admission, green = pushed toward discharge),
 * ranked by magnitude -- the most influential factors regardless of
 * direction, not two separate top-N lists.
 *
 * Color alone distinguishes direction here, which is not colorblind-safe
 * on its own; the legend and tooltip both label direction in text as a
 * mitigation (see TASKS.md Page 3 notes) -- a pattern-fill or icon-based
 * differentiator is flagged as follow-up work, not silently dropped.
 */
export function selectTopContributions(increased = [], decreased = [], maxFeatures = 8) {
  return [...increased, ...decreased]
    .slice()
    .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
    .slice(0, maxFeatures)
    .sort((a, b) => a.shap_value - b.shap_value)
}

function ContributionTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { feature, source_variable: sourceVariable, shap_value: shapValue } = payload[0].payload
  const increasing = shapValue >= 0

  return (
    <div className="rounded-lg border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
      <p className="font-medium">{feature}</p>
      <p className="text-muted-foreground">Source variable: {sourceVariable}</p>
      <p className={increasing ? 'text-destructive' : 'text-success'}>
        {increasing ? 'Increased' : 'Decreased'} risk — SHAP {shapValue.toFixed(3)}
      </p>
    </div>
  )
}

export default function FeatureContributionChart({ increased, decreased, maxFeatures = 8 }) {
  const data = selectTopContributions(increased, decreased, maxFeatures)

  if (data.length === 0) {
    return <p className="text-sm text-muted-foreground">No feature contributions to display.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(240, data.length * 40)}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
        <XAxis type="number" tick={{ fontSize: 12, fill: 'var(--muted-foreground)' }} stroke="var(--border)" />
        <YAxis
          type="category"
          dataKey="feature"
          width={160}
          tick={{ fontSize: 12, fill: 'var(--muted-foreground)' }}
          stroke="var(--border)"
        />
        <Tooltip content={<ContributionTooltip />} cursor={{ fill: 'var(--muted)' }} />
        <Bar dataKey="shap_value" radius={[4, 4, 4, 4]}>
          {data.map((entry) => (
            <Cell key={entry.feature} fill={entry.shap_value >= 0 ? INCREASE_COLOR : DECREASE_COLOR} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
