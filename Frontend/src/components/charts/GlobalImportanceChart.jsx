import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

/**
 * Converts the backend's { featureName: meanAbsShap } object into a
 * sorted array Recharts can consume. The backend already returns it
 * sorted descending, but object key order isn't a contract worth relying
 * on, so this re-sorts defensively.
 */
export function toChartData(importanceByFeature = {}) {
  return Object.entries(importanceByFeature)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

function ImportanceTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0].payload

  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs font-medium text-popover-foreground shadow-lg">
      <p className="font-bold text-primary">{name}</p>
      <p className="text-muted-foreground mt-0.5">Mean |SHAP| Impact: <span className="font-mono text-foreground font-semibold">{value.toFixed(4)}</span></p>
    </div>
  )
}

export default function GlobalImportanceChart({ data }) {
  const chartData = toChartData(data)

  if (chartData.length === 0) {
    return <p className="text-sm text-muted-foreground">No importance data to display.</p>
  }

  const maxVal = chartData[0]?.value || 1

  return (
    <ResponsiveContainer width="100%" height={Math.max(260, chartData.length * 36)}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
        <XAxis type="number" tick={{ fontSize: 11, fill: 'var(--muted-foreground)' }} stroke="var(--border)" />
        <YAxis
          type="category"
          dataKey="name"
          width={170}
          tick={{ fontSize: 11, fill: 'var(--foreground)' }}
          stroke="var(--border)"
        />
        <Tooltip content={<ImportanceTooltip />} cursor={{ fill: 'var(--muted)', opacity: 0.5 }} />
        <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={20}>
          {chartData.map((entry, index) => {
            // Top 3 features get enhanced primary emphasis
            const isTop3 = index < 3
            return (
              <Cell
                key={`cell-${index}`}
                fill={isTop3 ? 'oklch(0.47 0.16 258)' : 'oklch(0.65 0.12 258)'}
                opacity={0.7 + (entry.value / maxVal) * 0.3}
              />
            )
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
