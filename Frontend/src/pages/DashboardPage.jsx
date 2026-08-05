import { Activity, ArrowRight, CircleCheck, CircleX, Database, LayoutDashboard, Lightbulb, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import PageHeader from '@/components/PageHeader'
import Reveal from '@/components/Reveal'
import StatTile from '@/components/StatTile'
import PredictionsTable from '@/components/PredictionsTable'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { getDatabaseHealth, getLiveness, getModelHealth } from '@/services/healthApi'
import { listPredictions } from '@/services/historyApi'
import { useApiRequest } from '@/hooks/useApiRequest'
import { formatPercentage } from '@/utils/formatPercentage'

function HealthStatTile({ label, icon, apiFunction, renderValue }) {
  const { data, loading, error, execute } = useApiRequest(apiFunction, { immediate: true })

  if (error) {
    return (
      <Card size="sm">
        <CardContent className="flex items-start justify-between gap-3">
          <div className="space-y-1.5">
            <p className="text-sm text-muted-foreground">{label}</p>
            <button
              type="button"
              onClick={execute}
              className="text-sm font-medium text-destructive underline underline-offset-2"
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

/**
 * Turns the same 5 recently-fetched predictions the stat tiles and table
 * already display into one plain-language line -- reusing real data more
 * richly, not fabricating a new metric or calling a new endpoint.
 */
function buildDashboardInsight(predictions) {
  if (!predictions || predictions.length === 0) return null
  const highRiskCount = predictions.filter((prediction) => prediction.risk_category === 'high').length
  if (highRiskCount === 0) {
    return `None of the last ${predictions.length} prediction${predictions.length === 1 ? '' : 's'} were flagged high risk.`
  }
  return `${highRiskCount} of the last ${predictions.length} predictions ${highRiskCount === 1 ? 'was' : 'were'} flagged high risk.`
}

export default function DashboardPage() {
  const { data, loading, error, execute } = useApiRequest(() => listPredictions(5), { immediate: true })

  const admissionRate =
    data && data.length > 0
      ? data.filter((prediction) => prediction.predicted_admission).length / data.length
      : null
  const insight = buildDashboardInsight(data)

  return (
    <div className="space-y-8">
      <PageHeader
        icon={LayoutDashboard}
        title="Dashboard"
        description="Emergency Department admission prediction & explainability, at a glance."
      >
        <Button asChild>
          <Link to="/app/predict">
            New Prediction
            <ArrowRight />
          </Link>
        </Button>
      </PageHeader>

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
          <Alert>
            <Lightbulb />
            <AlertDescription className="text-foreground">{insight}</AlertDescription>
          </Alert>
        </Reveal>
      )}

      <Reveal delay={120}>
        <Card>
          <CardHeader>
            <CardTitle>Recent predictions</CardTitle>
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
