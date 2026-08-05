import { useState } from 'react'
import { ClipboardPlus, Sparkles } from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import PatientRecordForm from '@/components/forms/PatientRecordForm'
import PredictionResult from '@/components/PredictionResult'
import ErrorState from '@/components/ErrorState'
import { Card, CardContent } from '@/components/ui/card'
import { submitPrediction } from '@/services/predictionApi'
import { useApiRequest } from '@/hooks/useApiRequest'

function ResultPlaceholder() {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
        <div className="flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary">
          <ClipboardPlus className="size-5" />
        </div>
        <div className="space-y-1">
          <p className="font-medium text-foreground">No prediction yet</p>
          <p className="max-w-xs text-sm text-muted-foreground">
            Fill in the required vitals and submit the form to generate an admission prediction with its explanation.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

export default function PredictionPage() {
  const { data, loading, error, execute } = useApiRequest(submitPrediction)
  // Remount key for the result panel: bumped after every successful submission
  // so the entrance animation replays for each *new* prediction, not just the first.
  const [resultKey, setResultKey] = useState(0)

  const handleSubmit = async (payload) => {
    const result = await execute(payload)
    if (result) setResultKey((key) => key + 1)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        icon={ClipboardPlus}
        title="Patient Prediction"
        description="Enter patient information to generate an admission prediction."
      />

      <div className="flex gap-3 rounded-lg border bg-muted/40 p-4 text-sm text-muted-foreground">
        <Sparkles className="mt-0.5 size-4 shrink-0 text-primary" />
        <p>
          Every prediction is returned with a SHAP-based explanation of the specific patient factors that increased
          or decreased the estimated risk — shown alongside the result on the right.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <PatientRecordForm onSubmit={handleSubmit} isSubmitting={loading} />
        </div>

        <div className="space-y-6 lg:col-span-2">
          <div className="lg:sticky lg:top-6">
            {error && <ErrorState error={error} />}
            {!error && data && <PredictionResult key={resultKey} prediction={data} />}
            {!error && !data && <ResultPlaceholder />}
          </div>
        </div>
      </div>
    </div>
  )
}
