import { Cpu, Gauge, Lightbulb, Percent, TrendingUp } from 'lucide-react'
import RiskBadge from './RiskBadge'
import StatTile from './StatTile'
import FeatureContributionChart from './charts/FeatureContributionChart'
import { buildExplanationSummary } from './charts/explanationSummary'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatPercentage } from '../utils/formatPercentage'

export default function PredictionResult({ prediction }) {
  const {
    predicted_admission: predictedAdmission,
    admission_probability: admissionProbability,
    confidence_score: confidenceScore,
    base_rate_probability: baseRateProbability,
    risk_category: riskCategory,
    features_that_increased_risk: featuresThatIncreasedRisk,
    features_that_decreased_risk: featuresThatDecreasedRisk,
    model_name: modelName,
    model_version: modelVersion,
  } = prediction

  return (
    <Card className="animate-in fade-in slide-in-from-bottom-2 duration-300">
      <CardHeader>
        <CardTitle className="text-base">Prediction result</CardTitle>
        <div className="flex flex-wrap items-center gap-3 pt-1">
          <RiskBadge riskCategory={riskCategory} />
          <span className="text-xl font-semibold tracking-tight text-foreground">
            {predictedAdmission ? 'Predicted: Admission' : 'Predicted: No admission'}
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <StatTile label="Admission probability" icon={Percent} value={formatPercentage(admissionProbability)} />
          <StatTile label="Confidence" icon={Gauge} value={formatPercentage(confidenceScore)} />
          <StatTile label="Baseline rate" icon={TrendingUp} value={formatPercentage(baseRateProbability)} />
        </div>

        <div className="flex gap-3 rounded-lg border bg-muted/40 p-4">
          <Lightbulb className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
          <p className="text-sm text-foreground">
            {buildExplanationSummary({
              features_that_increased_risk: featuresThatIncreasedRisk,
              features_that_decreased_risk: featuresThatDecreasedRisk,
            })}
          </p>
        </div>

        <div>
          <h3 className="mb-3 text-sm font-medium text-foreground">Top contributing factors</h3>
          <FeatureContributionChart increased={featuresThatIncreasedRisk} decreased={featuresThatDecreasedRisk} />
          <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <span className="inline-block size-2 rounded-full bg-destructive" /> Increased risk
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block size-2 rounded-full bg-success" /> Decreased risk
            </span>
          </div>
        </div>

        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Cpu className="size-3.5" />
          {modelName} v{modelVersion}
        </p>
      </CardContent>
    </Card>
  )
}
