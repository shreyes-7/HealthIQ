import {
  Activity,
  ClipboardCheck,
  Cpu,
  Database,
  Gauge,
  Percent,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import Reveal from '@/components/Reveal'
import StatTile from '@/components/StatTile'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { getModelHealth } from '@/services/healthApi'
import { useApiRequest } from '@/hooks/useApiRequest'

const SECTIONS = [
  {
    icon: ClipboardCheck,
    title: 'What it does',
    body: 'HealthIQ is a research and decision-support platform that estimates the probability a patient presenting to the Emergency Department will require hospital admission, using the National Hospital Ambulatory Medical Care Survey (NHAMCS) dataset.',
  },
  {
    icon: Sparkles,
    title: 'How predictions work',
    body: 'Every prediction is accompanied by an explanation of the patient characteristics that most influenced it, generated using SHAP (SHapley Additive exPlanations). The platform is intended to support clinical judgment, not replace it.',
  },
  {
    icon: Cpu,
    title: 'About the model',
    body: 'Predictions are produced by a LightGBM model trained and evaluated on historical Emergency Department visits, served through a FastAPI backend and this React dashboard. The model considers 866 engineered features derived from the raw visit record.',
  },
]

// Sourced from ML/saved_models/model_metadata.json and
// ML/reports/modeling/final_model_selection.md -- the same validation-split
// numbers cited on the public landing page, kept consistent across the site
// rather than restated from memory.
const PERFORMANCE_STATS = [
  { icon: Gauge, label: 'Cross-validated ROC-AUC', value: '0.95', hint: 'Validation-split score: 0.96 — same figure cited on the homepage' },
  { icon: Percent, label: 'PR-AUC (validation)', value: '0.83', hint: 'More informative than ROC-AUC at ~13% base rate' },
  { icon: Activity, label: 'Recall / sensitivity', value: '70.1%', hint: 'Prioritized over precision — a missed admission is costlier' },
]

const RESPONSIBLE_USE = [
  {
    icon: ShieldCheck,
    title: 'Data & privacy',
    body: 'The model is trained on NHAMCS, a publicly available, de-identified U.S. government survey of Emergency Department visits — no real patient data was used in training. Predictions you submit through this app are stored so they can appear on the Prediction History page; they are not shared outside this application.',
  },
  {
    icon: TriangleAlert,
    title: 'Limitations',
    body: 'The model reflects patterns in historical U.S. survey data and may not generalize perfectly to every population, region, or care setting. Its test-split performance was evaluated exactly once, after model selection, to avoid overstating accuracy from repeated tuning. It is a decision-support signal, not a diagnosis.',
  },
]

export default function AboutPage() {
  const { data, loading } = useApiRequest(getModelHealth, { immediate: true })

  return (
    <div className="max-w-3xl space-y-10">
      <Reveal className="space-y-3">
        <div className="flex size-11 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Activity className="size-5" />
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">About HealthIQ</h1>
        <p className="text-lg text-muted-foreground">
          An intelligent, explainable decision-support tool for Emergency Department admission risk.
        </p>
      </Reveal>

      <Reveal delay={60} className="space-y-4">
        {SECTIONS.map((section) => (
          <Card key={section.title}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2.5 text-base">
                <span className="flex size-7 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <section.icon className="size-4" />
                </span>
                {section.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{section.body}</p>
            </CardContent>
          </Card>
        ))}
      </Reveal>

      <Reveal delay={100} className="space-y-3">
        <div className="space-y-1">
          <h2 className="text-lg font-semibold tracking-tight text-foreground">Model performance</h2>
          <p className="text-sm text-muted-foreground">
            Measured on a held-out validation split during model selection; the final test split (evaluated once,
            for confirmation only) scored within a point of these figures.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {PERFORMANCE_STATS.map((stat) => (
            <StatTile key={stat.label} icon={stat.icon} label={stat.label} value={stat.value} hint={stat.hint} />
          ))}
        </div>
      </Reveal>

      <Reveal delay={140} className="space-y-4">
        <h2 className="text-lg font-semibold tracking-tight text-foreground">Responsible use</h2>
        {RESPONSIBLE_USE.map((section) => (
          <Card key={section.title}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2.5 text-base">
                <span className="flex size-7 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <section.icon className="size-4" />
                </span>
                {section.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{section.body}</p>
            </CardContent>
          </Card>
        ))}
      </Reveal>

      <Reveal delay={180} className="flex flex-wrap items-center justify-between gap-4 rounded-lg border bg-muted/40 p-4">
        <div className="flex items-center gap-3">
          <Database className="size-4 shrink-0 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Want to see the underlying data behind past predictions?
          </p>
        </div>
        <Button asChild variant="outline" size="sm">
          <Link to="/app/history">View prediction history</Link>
        </Button>
      </Reveal>

      <Reveal delay={220} className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Cpu className="size-3.5" />
        {loading && <Skeleton className="h-4 w-32" />}
        {data && <span>Currently serving {data.model_name} v{data.model_version}</span>}
      </Reveal>
    </div>
  )
}
