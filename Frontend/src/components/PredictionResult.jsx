import { Cpu, Gauge, Lightbulb, Percent, TrendingUp, ShieldAlert, CheckCircle2, AlertTriangle, Stethoscope, FileText, ArrowRight } from 'lucide-react'
import RiskBadge from './RiskBadge'
import StatTile from './StatTile'
import FeatureContributionChart from './charts/FeatureContributionChart'
import { ProbabilityGauge } from './charts/ProbabilityGauge'
import { buildExplanationSummary } from './charts/explanationSummary'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatPercentage } from '../utils/formatPercentage'
import { Link } from 'react-router-dom'

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

  // Clinical Protocol Action Mapping
  let protocolTitle = 'ROUTINE DISCHARGE PROTOCOL'
  let protocolAction = 'Patient exhibits low probability of hospital admission. Proceed with routine outpatient discharge planning & symptomatic management.'
  let protocolBadge = 'bg-emerald-50 text-emerald-800 border-emerald-200'
  let ProtocolIcon = CheckCircle2

  if (riskCategory === 'high') {
    protocolTitle = 'EMERGENCY ADMISSION & ICU PROTOCOL'
    protocolAction = 'High admission risk detected (>75%). Immediate inpatient bed allocation, telemetry monitoring, and specialist consultation (CONSULT) required.'
    protocolBadge = 'bg-rose-50 text-rose-800 border-rose-200'
    ProtocolIcon = ShieldAlert
  } else if (riskCategory === 'moderate') {
    protocolTitle = 'URGENT OBSERVATION UNIT PROTOCOL'
    protocolAction = 'Moderate admission risk (40-74%). Hold in ED observation unit, repeat vital signs q30m, and request secondary physician assessment.'
    protocolBadge = 'bg-amber-50 text-amber-800 border-amber-200'
    ProtocolIcon = AlertTriangle
  }

  return (
    <Card className="animate-in fade-in slide-in-from-bottom-2 duration-300 border-blue-200 shadow-xl bg-white">
      <CardHeader className="pb-3 border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-base font-bold text-slate-900">Clinical Triage Outcome</CardTitle>
            <CardDescription className="text-xs text-slate-500">Real-time LightGBM Model Assessment</CardDescription>
          </div>
          <RiskBadge riskCategory={riskCategory} />
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-6">
        {/* Probability Gauge & Highlight Banner */}
        <div className="flex flex-col sm:flex-row items-center gap-6 rounded-2xl border border-slate-200 bg-slate-50/70 p-5">
          <ProbabilityGauge value={admissionProbability} size={120} strokeWidth={10} />
          <div className="space-y-2 text-center sm:text-left flex-1">
            <span className="text-xl font-extrabold tracking-tight text-slate-900">
              {predictedAdmission ? 'Predicted: Hospital Admission' : 'Predicted: Outpatient Discharge'}
            </span>
            <p className="text-xs text-slate-600 leading-relaxed">
              {predictedAdmission
                ? 'High statistical likelihood of hospital bed admission based on ED triage parameters.'
                : 'Favorable clinical presentation for outpatient management.'}
            </p>
            <div className="flex items-center justify-center sm:justify-start gap-2 pt-1">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${protocolBadge}`}>
                <ProtocolIcon className="size-3.5" /> {protocolTitle}
              </span>
            </div>
          </div>
        </div>

        {/* Clinical Action Recommendation Box */}
        <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-4 space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-900 uppercase tracking-wider">
            <Stethoscope className="size-4 text-blue-600" />
            <span>Recommended Clinical Next Steps:</span>
          </div>
          <p className="text-xs text-slate-700 leading-relaxed font-medium">
            {protocolAction}
          </p>
        </div>

        {/* Stat Tiles Row */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <StatTile label="Admission probability" icon={Percent} value={formatPercentage(admissionProbability)} />
          <StatTile label="Confidence" icon={Gauge} value={formatPercentage(confidenceScore)} />
          <StatTile label="Baseline rate" icon={TrendingUp} value={formatPercentage(baseRateProbability)} />
        </div>

        {/* Plain Language SHAP Insight */}
        <div className="flex gap-3 rounded-xl border border-amber-200 bg-amber-50/50 p-4">
          <Lightbulb className="mt-0.5 size-4 shrink-0 text-amber-600" />
          <div className="space-y-1 text-xs sm:text-sm text-slate-800">
            <p className="font-semibold text-slate-900">Key Risk Drivers Summary:</p>
            <p className="leading-relaxed">
              {buildExplanationSummary({
                features_that_increased_risk: featuresThatIncreasedRisk,
                features_that_decreased_risk: featuresThatDecreasedRisk,
              })}
            </p>
          </div>
        </div>

        {/* SHAP Contribution Chart */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-slate-900">SHAP Feature Attribution (Local Driver Weights)</h3>
            <Button asChild variant="ghost" size="sm" className="h-6 text-xs text-blue-600 hover:text-blue-800 p-0">
              <Link to="/app/explainability">
                Global SHAP Studio <ArrowRight className="size-3 ml-1" />
              </Link>
            </Button>
          </div>

          <FeatureContributionChart increased={featuresThatIncreasedRisk} decreased={featuresThatDecreasedRisk} />

          <div className="mt-3 flex items-center gap-4 text-xs text-slate-500 font-medium">
            <span className="flex items-center gap-1.5">
              <span className="inline-block size-2 rounded-full bg-rose-500" /> Increased risk factor
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block size-2 rounded-full bg-emerald-500" /> Decreased risk factor
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100">
          <span className="flex items-center gap-1.5">
            <Cpu className="size-3.5 text-blue-600" /> Powered by {modelName} v{modelVersion}
          </span>
          <span className="flex items-center gap-1">
            <FileText className="size-3.5" /> Logged to History
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
