import { Activity, ClipboardCheck, TriangleAlert } from 'lucide-react'
import { useState } from 'react'
import PageHeader from '@/components/PageHeader'
import PredictionsTable from '@/components/PredictionsTable'
import Reveal from '@/components/Reveal'
import StatTile from '@/components/StatTile'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { listPredictions } from '@/services/historyApi'
import { useApiRequest } from '@/hooks/useApiRequest'
import { filterPredictionsByRisk, sortPredictions, summarizePredictions } from '@/utils/predictionListUtils'
import { formatPercentage } from '@/utils/formatPercentage'

const MIN_LIMIT = 1
const MAX_LIMIT = 500
const LIMIT_PRESETS = [10, 25, 50, 100]
const RISK_FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'low', label: 'Low' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'high', label: 'High' },
]

export default function PredictionHistoryPage() {
  const [limit, setLimit] = useState(50)
  const [riskFilter, setRiskFilter] = useState('all')
  const [sortState, setSortState] = useState({ key: 'created_at', direction: 'desc' })
  const { data, loading, error, execute } = useApiRequest(listPredictions, { immediate: true, params: [limit] })

  function handleLimitPreset(value) {
    if (!value) return
    setLimit(Number(value))
  }

  function handleLimitCustom(event) {
    const value = Number(event.target.value)
    if (Number.isNaN(value)) return
    setLimit(Math.min(MAX_LIMIT, Math.max(MIN_LIMIT, value)))
  }

  function handleSortChange(key) {
    setSortState((previous) => {
      if (previous?.key === key) {
        return { key, direction: previous.direction === 'asc' ? 'desc' : 'asc' }
      }
      return { key, direction: 'desc' }
    })
  }

  const visiblePredictions = data
    ? sortPredictions(filterPredictionsByRisk(data, riskFilter), sortState)
    : []
  const summary = summarizePredictions(data)

  return (
    <div className="space-y-6">
      <PageHeader icon={Activity} title="Prediction History" description="Review previously generated predictions." />

      {data && data.length > 0 && (
        <Reveal className="grid gap-4 sm:grid-cols-3">
          <StatTile label="Records loaded" icon={Activity} value={summary.total} hint={`Most recent ${limit} requested`} />
          <StatTile
            label="Predicted admission rate"
            icon={ClipboardCheck}
            value={formatPercentage(summary.admissionRate)}
            hint="Across records loaded"
          />
          <StatTile
            label="High-risk share"
            icon={TriangleAlert}
            tone={summary.highRiskCount > 0 ? 'warning' : 'default'}
            value={formatPercentage(summary.highRiskRate)}
            hint={`${summary.highRiskCount} of ${summary.total} records`}
          />
        </Reveal>
      )}

      <div className="flex flex-wrap items-center gap-6">
        <div className="flex items-center gap-3">
          <Label className="text-sm text-muted-foreground">Show</Label>
          <ToggleGroup type="single" variant="outline" value={String(limit)} onValueChange={handleLimitPreset}>
            {LIMIT_PRESETS.map((preset) => (
              <ToggleGroupItem key={preset} value={String(preset)}>
                {preset}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          <Input
            type="number"
            min={MIN_LIMIT}
            max={MAX_LIMIT}
            value={limit}
            onChange={handleLimitCustom}
            className="w-20"
            aria-label="Custom number of records to show"
          />
        </div>

        <div className="flex items-center gap-3">
          <Label className="text-sm text-muted-foreground">Risk</Label>
          <ToggleGroup type="single" variant="outline" value={riskFilter} onValueChange={(v) => v && setRiskFilter(v)}>
            {RISK_FILTERS.map((option) => (
              <ToggleGroupItem key={option.value} value={option.value}>
                {option.label}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </div>
      </div>

      {loading && (
        <div className="space-y-3">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      )}
      {error && <ErrorState error={error} onRetry={() => execute(limit)} />}

      {data && data.length === 0 && <EmptyState message="No predictions have been made yet." />}

      {data && data.length > 0 && visiblePredictions.length === 0 && (
        <EmptyState message={`No ${riskFilter}-risk predictions in the last ${data.length} records.`} />
      )}

      {visiblePredictions.length > 0 && (
        <Reveal delay={80}>
          <Card>
            <CardContent>
              <PredictionsTable predictions={visiblePredictions} sortState={sortState} onSortChange={handleSortChange} />
            </CardContent>
          </Card>
        </Reveal>
      )}
    </div>
  )
}
