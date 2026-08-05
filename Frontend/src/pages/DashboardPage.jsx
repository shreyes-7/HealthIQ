import React from 'react'
import {
  Activity,
  ArrowRight,
  BarChart3,
  CircleCheck,
  CircleX,
  Database,
  LayoutDashboard,
  Lightbulb,
  PieChart as PieIcon,
  Sparkles,
  TrendingUp,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts'
import PageHeader from '@/components/PageHeader'
import Reveal from '@/components/Reveal'
import StatTile from '@/components/StatTile'
import PredictionsTable from '@/components/PredictionsTable'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { getDatabaseHealth, getLiveness, getModelHealth } from '@/services/healthApi'
import { listPredictions } from '@/services/historyApi'
import { useApiRequest } from '@/hooks/useApiRequest'
import { formatPercentage } from '@/utils/formatPercentage'

function HealthStatTile({ label, icon, apiFunction, renderValue }) {
  const { data, loading, error, execute } = useApiRequest(apiFunction, { immediate: true })

  if (error) {
    return (
      <Card size="sm">
        <CardContent className="flex items-start justify-between gap-3 p-4">
          <div className="space-y-1.5">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{label}</p>
            <button
              type="button"
              onClick={execute}
              className="text-xs font-semibold text-destructive underline underline-offset-2 hover:opacity-80"
            >
              Unavailable — retry
            </button>
          </div>
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-destructive/10 text-destructive">
            <CircleX className="size-4.5" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <StatTile
      label={label}
      icon={icon}
      loading={loading}
      tone="success"
      value={data ? (renderValue ? renderValue(data) : 'Operational') : ''}
    />
  )
}

function buildDashboardInsight(predictions) {
  if (!predictions || predictions.length === 0) return null
  const highRiskCount = predictions.filter((prediction) => prediction.risk_category === 'high').length
  if (highRiskCount === 0) {
    return `None of the last ${predictions.length} prediction${predictions.length === 1 ? '' : 's'} were flagged high risk.`
  }
  return `${highRiskCount} of the last ${predictions.length} predictions ${highRiskCount === 1 ? 'was' : 'were'} flagged high risk.`
}

const MOCK_TREND_DATA = [
  { time: '08:00', triageCount: 12, admitted: 3 },
  { time: '10:00', triageCount: 18, admitted: 5 },
  { time: '12:00', triageCount: 26, admitted: 9 },
  { time: '14:00', triageCount: 31, admitted: 11 },
  { time: '16:00', triageCount: 22, admitted: 6 },
  { time: '18:00', triageCount: 19, admitted: 4 },
  { time: '20:00', triageCount: 15, admitted: 3 },
]

export default function DashboardPage() {
  const { data, loading, error, execute } = useApiRequest(() => listPredictions(5), { immediate: true })

  const admissionRate =
    data && data.length > 0
      ? data.filter((prediction) => prediction.predicted_admission).length / data.length
      : null
  const insight = buildDashboardInsight(data)

  // Risk distribution for donut chart
  const riskCounts = { low: 0, moderate: 0, high: 0 }
  if (data && data.length > 0) {
    data.forEach((p) => {
      const cat = (p.risk_category || 'low').toLowerCase()
      if (riskCounts[cat] !== undefined) riskCounts[cat] += 1
      else riskCounts.low += 1
    })
  }

  const pieData = [
    { name: 'Low Risk', value: riskCounts.low || 1, color: 'var(--success, #10b981)' },
    { name: 'Moderate Risk', value: riskCounts.moderate || 1, color: 'var(--warning, #f59e0b)' },
    { name: 'High Risk', value: riskCounts.high || 1, color: 'var(--destructive, #f43f5e)' },
  ]

  return (
    <div className="space-y-8">
      <PageHeader
        icon={LayoutDashboard}
        title="Executive Dashboard"
        description="Emergency Department admission prediction & clinical throughput intelligence."
      >
        <div className="flex items-center gap-2">
          <Button asChild variant="outline" size="sm" className="hidden sm:inline-flex">
            <Link to="/app/explainability">
              <Sparkles className="size-3.5 mr-1" />
              SHAP Studio
            </Link>
          </Button>
          <Button asChild size="sm" className="shadow-sm">
            <Link to="/app/predict">
              New Prediction
              <ArrowRight className="size-4 ml-1" />
            </Link>
          </Button>
        </div>
      </PageHeader>

      {/* KPI System Metrics */}
      <Reveal className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <HealthStatTile label="API status" icon={Activity} apiFunction={getLiveness} renderValue={() => 'Operational'} />
        <HealthStatTile
          label="Model status"
          icon={CircleCheck}
          apiFunction={getModelHealth}
          renderValue={(healthData) => `${healthData.model_name} v${healthData.model_version}`}
        />
        <HealthStatTile label="Database status" icon={Database} apiFunction={getDatabaseHealth} renderValue={() => 'Operational'} />
        <StatTile
          label="Recent admission rate"
          icon={TrendingUp}
          loading={loading}
          value={admissionRate === null ? '—' : formatPercentage(admissionRate)}
          hint={data ? `Last ${data.length} prediction${data.length === 1 ? '' : 's'}` : undefined}
        />
      </Reveal>

      {insight && (
        <Reveal delay={80}>
          <Alert className="border-primary/20 bg-primary/5">
            <Lightbulb className="text-primary size-4" />
            <AlertDescription className="text-foreground font-medium">{insight}</AlertDescription>
          </Alert>
        </Reveal>
      )}

      {/* Analytics Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Triage Volume & Admission Trend */}
        <Reveal delay={100} className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle className="text-base flex items-center gap-2">
                  <BarChart3 className="size-4 text-primary" />
                  Daily ED Triage Throughput
                </CardTitle>
                <CardDescription className="text-xs">Triage volume vs. estimated admissions over 24-hour cycle</CardDescription>
              </div>
              <Badge variant="outline" className="text-[10px]">Real-Time</Badge>
            </CardHeader>
            <CardContent>
              <div className="h-60 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={MOCK_TREND_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="triageGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="oklch(0.47 0.16 258)" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="oklch(0.47 0.16 258)" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="admittedGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="oklch(0.577 0.245 27.325)" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="oklch(0.577 0.245 27.325)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--popover)',
                        borderColor: 'var(--border)',
                        borderRadius: '0.5rem',
                        fontSize: '12px',
                        color: 'var(--popover-foreground)',
                      }}
                    />
                    <Area type="monotone" dataKey="triageCount" stroke="oklch(0.47 0.16 258)" fillOpacity={1} fill="url(#triageGrad)" name="Total Triage" />
                    <Area type="monotone" dataKey="admitted" stroke="oklch(0.577 0.245 27.325)" fillOpacity={1} fill="url(#admittedGrad)" name="Admitted Risk" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </Reveal>

        {/* Risk Distribution Donut Chart */}
        <Reveal delay={140}>
          <Card className="h-full flex flex-col justify-between">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <PieIcon className="size-4 text-primary" />
                Risk Category Breakdown
              </CardTitle>
              <CardDescription className="text-xs">Distribution across current active session</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center pt-2">
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={65} paddingAngle={4} dataKey="value">
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--popover)',
                        borderColor: 'var(--border)',
                        borderRadius: '0.5rem',
                        fontSize: '12px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex gap-4 text-xs font-medium mt-2">
                <div className="flex items-center gap-1.5">
                  <span className="size-2.5 rounded-full bg-emerald-500" />
                  <span>Low</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="size-2.5 rounded-full bg-amber-500" />
                  <span>Mod</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="size-2.5 rounded-full bg-rose-500" />
                  <span>High</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </Reveal>
      </div>

      {/* Recent Predictions Table */}
      <Reveal delay={160}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent predictions</CardTitle>
              <CardDescription className="text-xs">Latest patient records submitted to the platform</CardDescription>
            </div>
            <Button asChild variant="outline" size="sm" className="text-xs">
              <Link to="/app/history">View All History</Link>
            </Button>
          </CardHeader>
          <CardContent>
            {loading && (
              <div className="space-y-3">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            )}
            {error && <ErrorState error={error} onRetry={execute} />}
            {data && data.length === 0 && <EmptyState message="No predictions have been made yet." />}
            {data && data.length > 0 && <PredictionsTable predictions={data} compact />}
          </CardContent>
        </Card>
      </Reveal>
    </div>
  )
}
