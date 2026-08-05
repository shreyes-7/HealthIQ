import { lazy, Suspense, useState } from 'react'
import {
  Activity,
  ArrowRight,
  ChevronDown,
  ClipboardPlus,
  Cpu,
  Database,
  Gauge,
  HeartPulse,
  LayoutDashboard,
  Lightbulb,
  Menu,
  Server,
  ShieldAlert,
  Sparkles,
  TrendingUp,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import Reveal from '@/components/Reveal'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetClose, SheetContent, SheetFooter, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Skeleton } from '@/components/ui/skeleton'

// Loaded on demand, same as every in-app page that renders it -- this keeps
// Recharts (pulled in by FeatureContributionChart) out of the eagerly
// loaded landing-page bundle.
const PredictionResult = lazy(() => import('@/components/PredictionResult'))

// Illustrative only -- feature names match the model's real SHAP output
// (verified against a live prediction), but the numbers are hand-picked to
// make a readable preview, not a real inference. Labelled as a sample in
// the UI so it can't be mistaken for a live result.
const SAMPLE_PREDICTION = {
  predicted_admission: true,
  admission_probability: 0.78,
  confidence_score: 0.91,
  base_rate_probability: 0.13,
  risk_category: 'high',
  features_that_increased_risk: [
    { feature: 'RFV53D__frequency', source_variable: 'RFV53D', feature_value: 3, shap_value: 0.62 },
    { feature: 'ARRTIME__frequency', source_variable: 'ARRTIME', feature_value: 2, shap_value: 0.54 },
    { feature: 'RX1V2C1__frequency', source_variable: 'RX1V2C1', feature_value: 1, shap_value: 0.41 },
    { feature: 'RFV13D__frequency', source_variable: 'RFV13D', feature_value: 4, shap_value: 0.33 },
    { feature: 'RX1CAT1__frequency', source_variable: 'RX1CAT1', feature_value: 2, shap_value: 0.29 },
  ],
  features_that_decreased_risk: [
    { feature: 'EHRINSE__Missing', source_variable: 'EHRINSE', feature_value: 0, shap_value: -0.35 },
    { feature: 'CONSULT__Yes', source_variable: 'CONSULT', feature_value: 1, shap_value: -0.22 },
  ],
  model_name: 'lightgbm',
  model_version: '1.0.0',
}

const SECTION_LINKS = [
  { href: '#features', label: 'Product' },
  { href: '#how-it-works', label: 'How it works' },
  { href: '#trust', label: 'About the model' },
  { href: '#faq', label: 'FAQ' },
]

const METRICS = [
  {
    icon: Gauge,
    value: '0.95',
    label: 'Cross-validated ROC-AUC',
    hint: 'LightGBM, 5-fold cross-validation',
  },
  {
    icon: Sparkles,
    value: 'Every prediction',
    label: 'Ships with a SHAP explanation',
    hint: 'No black-box scores',
  },
  {
    icon: Database,
    value: 'NHAMCS',
    label: 'Trained on real ED visit data',
    hint: 'National Hospital Ambulatory Medical Care Survey',
  },
]

const FEATURES = [
  {
    icon: Gauge,
    title: 'Real-time risk scoring',
    body: 'Enter vitals and triage details and get a calibrated admission probability in seconds — not a static, rule-based score.',
  },
  {
    icon: Lightbulb,
    title: 'Explainable by design',
    body: 'Every prediction ships with the specific patient factors that increased or decreased risk. Explainability is a required feature here, not an add-on.',
  },
  {
    icon: HeartPulse,
    title: 'Built for time-pressured clinicians',
    body: 'A focused, two-column workflow keeps the form and the result on screen together, so there is no scrolling to find the answer.',
  },
  {
    icon: TrendingUp,
    title: 'Rigorously validated',
    body: 'Cross-validated and held-out test performance, tracked model versioning, and a live model-health check — not a one-off notebook result.',
  },
]

const STEPS = [
  {
    step: '01',
    title: 'Enter patient vitals & triage info',
    body: 'Demographics, vitals, triage level, and arrival method — the fields already captured at the point of triage.',
  },
  {
    step: '02',
    title: 'Get a calibrated risk score',
    body: 'The LightGBM model returns an admission probability, a confidence score, and a low / moderate / high risk category in real time.',
  },
  {
    step: '03',
    title: 'Review the explanation',
    body: 'A SHAP-based breakdown shows exactly which patient factors increased or decreased the predicted risk.',
  },
]

const TECH_STACK = [
  { icon: Server, label: 'FastAPI backend' },
  { icon: Cpu, label: 'LightGBM model' },
  { icon: Lightbulb, label: 'SHAP explainability' },
  { icon: Database, label: 'NHAMCS dataset' },
  { icon: LayoutDashboard, label: 'React dashboard' },
]

const FAQS = [
  {
    question: 'Is HealthIQ used to make real clinical decisions?',
    answer:
      'No. HealthIQ is a research and decision-support tool intended to support clinical judgment, not replace it. It is not a diagnostic device.',
  },
  {
    question: 'What data was the model trained on?',
    answer:
      'The model is trained and evaluated on Emergency Department visit records from the National Hospital Ambulatory Medical Care Survey (NHAMCS), a nationally representative U.S. survey of ED visits.',
  },
  {
    question: 'How are predictions explained?',
    answer:
      'Every prediction is accompanied by a SHAP (SHapley Additive exPlanations) breakdown showing which patient factors increased or decreased the predicted admission risk, alongside a plain-language summary.',
  },
  {
    question: 'What model powers the predictions?',
    answer:
      'A LightGBM gradient-boosted model, selected after comparing several candidate models on cross-validated performance. It is served through a FastAPI backend.',
  },
  {
    question: 'Can I see past predictions?',
    answer: 'Yes — every prediction is stored and available on the Prediction History page, with sortable and filterable results.',
  },
]

const APP_LINKS = [
  { to: '/app', label: 'Dashboard' },
  { to: '/app/predict', label: 'Prediction' },
  { to: '/app/explainability', label: 'Explainability' },
  { to: '/app/history', label: 'Prediction History' },
  { to: '/app/about', label: 'About' },
]

function Logo({ className = '' }) {
  return (
    <Link
      to="/"
      className={`flex items-center gap-2 rounded-md outline-none focus-visible:ring-3 focus-visible:ring-ring/50 ${className}`}
    >
      <div className="flex size-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
        <Activity className="size-4" />
      </div>
      <span className="text-base font-semibold tracking-tight text-foreground">HealthIQ</span>
    </Link>
  )
}

function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/85 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <Logo />
        <nav aria-label="Page sections" className="hidden items-center gap-6 text-sm text-muted-foreground md:flex">
          {SECTION_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-md outline-none transition-colors hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              {link.label}
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <Button asChild size="sm">
            <Link to="/app">
              Launch app
              <ArrowRight />
            </Link>
          </Button>
          <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon" className="md:hidden" aria-label="Open menu">
                <Menu />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              <SheetHeader>
                <SheetTitle>Menu</SheetTitle>
              </SheetHeader>
              <nav aria-label="Mobile" className="flex flex-1 flex-col gap-1 overflow-y-auto px-4">
                <p className="px-2 pb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">On this page</p>
                {SECTION_LINKS.map((link) => (
                  <SheetClose asChild key={link.href}>
                    <a href={link.href} className="rounded-md px-2 py-2 text-sm text-foreground hover:bg-muted">
                      {link.label}
                    </a>
                  </SheetClose>
                ))}
                <Separator className="my-3" />
                <p className="px-2 pb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">Application</p>
                {APP_LINKS.map((link) => (
                  <SheetClose asChild key={link.to}>
                    <Link to={link.to} className="flex items-center gap-2 rounded-md px-2 py-2 text-sm text-foreground hover:bg-muted">
                      <LayoutDashboard className="size-4 text-muted-foreground" />
                      {link.label}
                    </Link>
                  </SheetClose>
                ))}
              </nav>
              <SheetFooter>
                <SheetClose asChild>
                  <Button asChild>
                    <Link to="/app">
                      Launch app
                      <ArrowRight />
                    </Link>
                  </Button>
                </SheetClose>
              </SheetFooter>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}

function Hero() {
  return (
    <section className="relative mx-auto max-w-4xl overflow-hidden px-6 pt-20 pb-16 text-center sm:pt-28 sm:pb-24">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 -top-16 -z-10 mx-auto h-72 w-full max-w-[36rem] rounded-full bg-primary/10 blur-3xl"
      />
      <Reveal>
        <Badge variant="secondary" className="gap-1.5 rounded-full px-3 py-1 text-xs">
          <Sparkles data-icon="inline-start" className="size-3.5 text-primary" />
          Decision support · NHAMCS-trained
        </Badge>
        <h1 className="mt-6 text-3xl font-semibold tracking-tight text-balance text-foreground sm:text-4xl">
          Emergency Department admission risk — explained, not just predicted.
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-balance text-muted-foreground">
          HealthIQ estimates a patient&apos;s probability of hospital admission at the point of ED triage, and shows
          exactly which clinical factors drove that estimate — so the number is something a clinician can reason
          about, not a black box.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link to="/app">
              Launch the app
              <ArrowRight />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <a href="#how-it-works">See how it works</a>
          </Button>
        </div>
      </Reveal>
    </section>
  )
}

function MetricStrip() {
  return (
    <section aria-label="Model performance highlights" className="mx-auto max-w-5xl px-6 pb-20">
      <div className="grid gap-4 sm:grid-cols-3">
        {METRICS.map((metric, index) => (
          <Reveal key={metric.label} delay={index * 80}>
            <Card className="h-full transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
              <CardContent className="flex items-start gap-3">
                <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <metric.icon className="size-4.5" />
                </div>
                <div className="space-y-0.5">
                  <p className="text-xl font-semibold tracking-tight text-foreground">{metric.value}</p>
                  <p className="text-sm font-medium text-foreground">{metric.label}</p>
                  <p className="text-xs text-muted-foreground">{metric.hint}</p>
                </div>
              </CardContent>
            </Card>
          </Reveal>
        ))}
      </div>
    </section>
  )
}

function ProductPreview() {
  return (
    <section id="preview" aria-label="Sample prediction preview" className="mx-auto max-w-3xl px-6 pb-20">
      <Reveal className="space-y-2 text-center">
        <Badge variant="outline" className="mx-auto">
          Sample prediction
        </Badge>
        <h2 className="text-2xl font-semibold tracking-tight text-foreground">See what a prediction looks like</h2>
        <p className="mx-auto max-w-md text-muted-foreground">
          The same result panel and SHAP breakdown a clinician sees inside the app — illustrative, not a live
          prediction.
        </p>
      </Reveal>
      <div className="mt-8">
        <Suspense fallback={<Skeleton className="h-96 w-full" />}>
          <PredictionResult prediction={SAMPLE_PREDICTION} />
        </Suspense>
      </div>
    </section>
  )
}

function Features() {
  return (
    <section id="features" className="scroll-mt-16 border-t border-border/60 bg-muted/30 py-20">
      <div className="mx-auto max-w-5xl px-6">
        <Reveal className="max-w-xl space-y-2">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">
            A prediction is only useful if you can trust it
          </h2>
          <p className="text-muted-foreground">Every part of HealthIQ is built around that one requirement.</p>
        </Reveal>
        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {FEATURES.map((feature, index) => (
            <Reveal key={feature.title} delay={index * 80}>
              <Card className="h-full transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <feature.icon className="size-4 text-primary" />
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{feature.body}</p>
                </CardContent>
              </Card>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-16 py-20">
      <div className="mx-auto max-w-5xl px-6">
        <Reveal className="max-w-xl space-y-2">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">How it works</h2>
          <p className="text-muted-foreground">From triage fields to an explained risk score in three steps.</p>
        </Reveal>
        <ol className="mt-10 grid gap-8 sm:grid-cols-3">
          {STEPS.map((step, index) => (
            <Reveal key={step.step} as="li" delay={index * 100} className="space-y-2">
              <span className="text-sm font-semibold tracking-tight text-primary">{step.step}</span>
              <h3 className="text-base font-medium text-foreground">{step.title}</h3>
              <p className="text-sm text-muted-foreground">{step.body}</p>
            </Reveal>
          ))}
        </ol>
      </div>
    </section>
  )
}

function TechStack() {
  return (
    <section aria-label="Technology stack" className="border-t border-border/60 py-16">
      <div className="mx-auto max-w-5xl px-6 text-center">
        <Reveal>
          <p className="text-sm font-medium text-muted-foreground">Built on real infrastructure, not a demo stack</p>
        </Reveal>
        <Reveal delay={100} className="mt-6 flex flex-wrap items-center justify-center gap-3">
          {TECH_STACK.map((tech) => (
            <span
              key={tech.label}
              className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-foreground transition-colors hover:border-primary/40"
            >
              <tech.icon className="size-4 text-primary" />
              {tech.label}
            </span>
          ))}
        </Reveal>
      </div>
    </section>
  )
}

function TrustSection() {
  return (
    <section id="trust" className="scroll-mt-16 border-t border-border/60 bg-muted/30 py-20">
      <div className="mx-auto max-w-3xl space-y-6 px-6">
        <Reveal className="space-y-2">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">
            Built on real clinical data, rigorously validated
          </h2>
          <p className="text-muted-foreground">
            Predictions are produced by a LightGBM model trained and evaluated on historical Emergency Department
            visits from the National Hospital Ambulatory Medical Care Survey, served through a FastAPI backend and
            this dashboard. Every explanation is generated with SHAP (SHapley Additive exPlanations).
          </p>
        </Reveal>
        <Reveal delay={80}>
          <Alert variant="warning">
            <ShieldAlert />
            <AlertDescription className="text-warning/90">
              HealthIQ is a research and decision-support tool. It is intended to support clinical judgment, not
              replace it.
            </AlertDescription>
          </Alert>
        </Reveal>
        <Reveal delay={140}>
          <Button asChild variant="link" className="h-auto p-0 text-sm">
            <Link to="/app/about">
              Read more about the model
              <ArrowRight />
            </Link>
          </Button>
        </Reveal>
      </div>
    </section>
  )
}

function FaqItem({ question, answer }) {
  const [open, setOpen] = useState(false)

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <Card>
        <CollapsibleTrigger asChild>
          <button type="button" className="flex w-full items-center justify-between gap-4 p-5 text-left">
            <span className="text-sm font-medium text-foreground">{question}</span>
            <ChevronDown
              className={`size-4 shrink-0 text-muted-foreground transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
            />
          </button>
        </CollapsibleTrigger>
        <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
          <div className="border-t px-5 pt-4 pb-5 text-sm text-muted-foreground">{answer}</div>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  )
}

function Faq() {
  return (
    <section id="faq" className="scroll-mt-16 py-20">
      <div className="mx-auto max-w-3xl px-6">
        <Reveal className="max-w-xl space-y-2">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">Frequently asked questions</h2>
        </Reveal>
        <div className="mt-8 space-y-3">
          {FAQS.map((faq, index) => (
            <Reveal key={faq.question} delay={index * 60}>
              <FaqItem {...faq} />
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

function FinalCta() {
  return (
    <section className="border-t border-border/60 py-20">
      <Reveal className="mx-auto flex max-w-3xl flex-col items-center gap-5 px-6 text-center">
        <div className="flex size-11 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <ClipboardPlus className="size-5" />
        </div>
        <h2 className="text-2xl font-semibold tracking-tight text-foreground">Ready to see it in action?</h2>
        <p className="max-w-md text-muted-foreground">
          Open the dashboard, generate a prediction, and see the explanation behind it.
        </p>
        <Button asChild size="lg">
          <Link to="/app">
            Launch the app
            <ArrowRight />
          </Link>
        </Button>
      </Reveal>
    </section>
  )
}

function SiteFooter() {
  return (
    <footer className="border-t border-border/60 py-10">
      <div className="mx-auto flex max-w-5xl flex-col gap-8 px-6 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <Logo />
          <p className="max-w-xs text-sm text-muted-foreground">
            Explainable Emergency Department admission risk prediction, built on the NHAMCS dataset.
          </p>
        </div>
        <nav aria-label="Application pages" className="flex flex-wrap gap-6 text-sm text-muted-foreground">
          {APP_LINKS.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="rounded-md outline-none transition-colors hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
      <div className="mx-auto mt-8 max-w-5xl px-6 text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} HealthIQ. A research and decision-support tool — not a diagnostic device.
      </div>
    </footer>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-svh bg-background text-foreground">
      <SiteHeader />
      <main>
        <Hero />
        <MetricStrip />
        <ProductPreview />
        <Features />
        <HowItWorks />
        <TechStack />
        <TrustSection />
        <Faq />
        <FinalCta />
      </main>
      <SiteFooter />
    </div>
  )
}
