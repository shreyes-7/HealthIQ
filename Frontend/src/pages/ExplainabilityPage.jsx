import { Lightbulb, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { getGlobalExplanation } from '@/services/explainApi'
import { useApiRequest } from '@/hooks/useApiRequest'
import ErrorState from '@/components/ErrorState'
import PageHeader from '@/components/PageHeader'
import Reveal from '@/components/Reveal'
import GlobalImportanceChart from '@/components/charts/GlobalImportanceChart'
import { buildGlobalInsightSummary } from '@/components/charts/globalInsightSummary'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'

const MIN_TOP_N = 1
const MAX_TOP_N = 866
const PRESETS = [5, 10, 20, 50]

function buildComputedNote(data) {
  if (!data) return 'Computed once over the validation split — not recomputed per prediction.'
  const split = data.computed_on ? data.computed_on.replace(/_/g, ' ') : 'the validation split'
  const rows = typeof data.n_rows === 'number' ? data.n_rows.toLocaleString() : null
  return rows
    ? `Computed once over ${rows} rows of the ${split} — not recomputed per prediction.`
    : `Computed once over the ${split} — not recomputed per prediction.`
}

export default function ExplainabilityPage() {
  const [topN, setTopN] = useState(20)
  const { data, loading, error, execute } = useApiRequest(getGlobalExplanation, { immediate: true, params: [topN] })

  function handlePresetChange(value) {
    if (!value) return
    setTopN(Number(value))
  }

  function handleCustomChange(event) {
    const value = Number(event.target.value)
    if (Number.isNaN(value)) return
    setTopN(Math.min(MAX_TOP_N, Math.max(MIN_TOP_N, value)))
  }

  return (
    <div className="space-y-6">
      <PageHeader
        icon={Sparkles}
        title="Model Explainability"
        description="Explore which patient characteristics most influence the model overall."
        note={buildComputedNote(data)}
      />

      <p className="max-w-3xl text-sm text-muted-foreground">
        This is the model&apos;s <span className="font-medium text-foreground">global</span> view — which
        characteristics matter most on average, across every patient in the validation data. It is a different,
        complementary view from the <span className="font-medium text-foreground">local</span> explanation shown
        with an individual prediction, which reflects only that one patient&apos;s factors.
      </p>

      <div className="flex flex-wrap items-center gap-4">
        <ToggleGroup type="single" variant="outline" value={String(topN)} onValueChange={handlePresetChange}>
          {PRESETS.map((preset) => (
            <ToggleGroupItem key={preset} value={String(preset)}>
              Top {preset}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
        <div className="flex items-center gap-2">
          <Label htmlFor="top-n-custom" className="text-sm text-muted-foreground">
            Custom
          </Label>
          <Input
            id="top-n-custom"
            type="number"
            min={MIN_TOP_N}
            max={MAX_TOP_N}
            value={topN}
            onChange={handleCustomChange}
            className="w-20"
          />
        </div>
      </div>

      {loading && (
        <div className="space-y-6">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-80 w-full" />
        </div>
      )}
      {error && <ErrorState error={error} onRetry={() => execute(topN)} />}

      {data && (
        <Reveal className="space-y-6">
          <div className="flex gap-3 rounded-lg border bg-muted/40 p-4">
            <Lightbulb className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
            <p className="text-sm text-foreground">{buildGlobalInsightSummary(data.top_source_variables)}</p>
          </div>

          <Tabs defaultValue="feature">
            <TabsList>
              <TabsTrigger value="feature">By encoded feature</TabsTrigger>
              <TabsTrigger value="source">By source variable</TabsTrigger>
            </TabsList>
            <TabsContent value="feature">
              <Card>
                <CardHeader>
                  <CardTitle>Top {topN} encoded features</CardTitle>
                  <CardDescription>
                    Mean absolute SHAP value per individual encoded feature (e.g. one option of a categorical field).
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <GlobalImportanceChart data={data.top_features} />
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="source">
              <Card>
                <CardHeader>
                  <CardTitle>Top {topN} source variables</CardTitle>
                  <CardDescription>
                    Encoded features grouped back to the original clinical variable they came from.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <GlobalImportanceChart data={data.top_source_variables} />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </Reveal>
      )}
    </div>
  )
}
