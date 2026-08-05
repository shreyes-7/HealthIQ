import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const BAR_COLOR = 'var(--primary)'

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
    <div className="rounded-lg border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
      <p className="font-medium">{name}</p>
      <p className="text-muted-foreground">Mean |SHAP|: {value.toFixed(3)}</p>
    </div>
  )
}

export default function GlobalImportanceChart({ data }) {
  const chartData = toChartData(data)

  if (chartData.length === 0) {
    return <p className="text-sm text-muted-foreground">No importance data to display.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(240, chartData.length * 32)}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
        <XAxis type="number" tick={{ fontSize: 12, fill: 'var(--muted-foreground)' }} stroke="var(--border)" />
        <YAxis
          type="category"
          dataKey="name"
          width={160}
          tick={{ fontSize: 12, fill: 'var(--muted-foreground)' }}
          stroke="var(--border)"
        />
        <Tooltip content={<ImportanceTooltip />} cursor={{ fill: 'var(--muted)' }} />
        <Bar dataKey="value" fill={BAR_COLOR} radius={[4, 4, 4, 4]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
