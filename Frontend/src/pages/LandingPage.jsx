import { lazy, Suspense, useState } from 'react'
import {
  Activity,
  ArrowRight,
  ChevronDown,
  ClipboardPlus,
  Cpu,
  Database,
  FileText,
  Gauge,
  HeartPulse,
  LayoutDashboard,
  Lightbulb,
  Lock,
  Menu,
  Server,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  UserCheck,
  Zap,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import Reveal from '@/components/Reveal'
import { BentoGrid, BentoCard } from '@/components/ui/BentoGrid'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetClose, SheetContent, SheetFooter, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Skeleton } from '@/components/ui/skeleton'

const PredictionResult = lazy(() => import('@/components/PredictionResult'))

function GithubIcon({ className = 'size-4' }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
      />
    </svg>
  )
}

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
  { href: '#preview', label: 'Platform Showcase' },
  { href: '#bento', label: 'Capabilities' },
  { href: '#journey', label: 'Patient Workflow' },
  { href: '#architecture', label: 'Architecture' },
  { href: '#faq', label: 'FAQ' },
]

const METRICS = [
  {
    icon: Gauge,
    value: '0.95 ROC-AUC',
    label: 'Model Accuracy',
    hint: 'Cross-validated LightGBM on 30k+ records',
  },
  {
    icon: Zap,
    value: '< 18ms Latency',
    label: 'Real-time Inference',
    hint: 'Sub-second FastAPI response time',
  },
  {
    icon: Sparkles,
    value: '100% Explainable',
    label: 'SHAP Feature Attribution',
    hint: 'Zero black-box predictions',
  },
  {
    icon: Database,
    value: 'NHAMCS Verified',
    label: 'CDC Clinical Dataset',
    hint: 'National ED Ambulatory Survey',
  },
]

const FAQS = [
  {
    question: 'Is HealthIQ used to make final clinical admission decisions?',
    answer:
      'No. HealthIQ is an AI decision-support tool designed to assist healthcare professionals by providing objective probability estimates and feature explanations. Final clinical judgment remains entirely with the attending physician.',
  },
  {
    question: 'What dataset was used to train the prediction model?',
    answer:
      'The model is trained on the CDC National Hospital Ambulatory Medical Care Survey (NHAMCS), representing tens of thousands of Emergency Department visits with comprehensive demographics, vitals, and clinical outcomes.',
  },
  {
    question: 'How does SHAP explainability work in HealthIQ?',
    answer:
      'SHAP (SHapley Additive exPlanations) measures how much each specific input feature (e.g., elevated pulse rate, triage level 2, or lab test presence) pushed the admission probability above or below the baseline population average.',
  },
  {
    question: 'Can HealthIQ be integrated with EHR systems?',
    answer:
      'Yes. HealthIQ exposes standard REST APIs via FastAPI and accepts structured JSON payloads matching standard HL7/FHIR triage fields.',
  },
  {
    question: 'Is patient data stored or logged?',
    answer:
      'HealthIQ logs prediction metadata and outcome metrics for historical audit trails without storing identifiable personal health information (PHI), following HIPAA guidelines.',
  },
]

function Logo({ className = '' }) {
  return (
    <Link
      to="/"
      className={`flex items-center gap-2.5 rounded-lg outline-none focus-visible:ring-2 focus-visible:ring-ring ${className}`}
    >
      <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
        <Activity className="size-4.5" />
      </div>
      <div className="flex flex-col">
        <span className="text-base font-bold tracking-tight text-slate-900 leading-none">HealthIQ</span>
        <span className="text-[10px] font-medium text-slate-500 leading-tight">Clinical AI Platform</span>
      </div>
    </Link>
  )
}

function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-md transition-all">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Logo />

        <nav aria-label="Page sections" className="hidden items-center gap-6 text-sm font-medium text-slate-600 lg:flex">
          {SECTION_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="transition-colors hover:text-slate-900 focus-visible:outline-none"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <Button asChild size="sm" className="hidden sm:inline-flex shadow-sm bg-blue-600 hover:bg-blue-700">
            <Link to="/app">
              Launch Console
              <ArrowRight className="size-4 ml-1" />
            </Link>
          </Button>

          {/* Mobile Sheet Nav */}
          <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon" className="lg:hidden" aria-label="Open menu">
                <Menu className="size-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-80">
              <SheetHeader className="text-left pb-4">
                <Logo />
              </SheetHeader>
              <nav className="flex flex-col gap-2 py-4">
                <p className="px-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Navigation</p>
                {SECTION_LINKS.map((link) => (
                  <SheetClose asChild key={link.href}>
                    <a href={link.href} className="rounded-lg px-3 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100">
                      {link.label}
                    </a>
                  </SheetClose>
                ))}
                <Separator className="my-3" />
                <p className="px-2 text-xs font-semibold uppercase tracking-wider text-slate-500">App Console</p>
                <SheetClose asChild>
                  <Link to="/app" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50">
                    <LayoutDashboard className="size-4" />
                    Dashboard Console
                  </Link>
                </SheetClose>
                <SheetClose asChild>
                  <Link to="/app/predict" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100">
                    <ClipboardPlus className="size-4" />
                    Triage Prediction Form
                  </Link>
                </SheetClose>
              </nav>
              <SheetFooter className="mt-auto">
                <SheetClose asChild>
                  <Button asChild className="w-full bg-blue-600 hover:bg-blue-700">
                    <Link to="/app">Launch Platform</Link>
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
    <section className="relative overflow-hidden pt-20 pb-20 lg:pt-28 lg:pb-28 bg-gradient-to-b from-slate-50 via-blue-50/20 to-white">
      {/* Background Decorative Gradients & Grid */}
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(59,130,246,0.12),rgba(255,255,255,0))]" />

      <div className="mx-auto max-w-4xl px-6 text-center">
        <Reveal>
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-xs font-semibold text-blue-700 shadow-xs">
            <Sparkles className="size-3.5" />
            <span>Next-Gen Emergency Department Triage AI</span>
          </div>

          <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl text-balance">
            Emergency Admission Risk. <br />
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-teal-600 bg-clip-text text-transparent">
              Explained, Not Just Predicted.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-base sm:text-lg text-slate-600 leading-relaxed text-balance">
            HealthIQ gives clinical teams instant, calibrated hospital admission probabilities at the point of ED triage—backed by transparent SHAP feature attributions for every single outcome.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Button asChild size="lg" className="h-12 px-8 text-base shadow-lg shadow-blue-500/25 active:scale-95 transition-transform bg-blue-600 hover:bg-blue-700">
              <Link to="/app/predict">
                Start Triage Prediction
                <ArrowRight className="size-5 ml-2" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="h-12 px-8 text-base active:scale-95 transition-transform border-slate-300">
              <a href="#preview">Explore Live Demo</a>
            </Button>
          </div>
        </Reveal>

        {/* Hero Stat Strip */}
        <div className="mt-16 grid grid-cols-2 gap-4 sm:grid-cols-4 lg:gap-6">
          {METRICS.map((metric, idx) => (
            <Reveal key={metric.label} delay={idx * 70}>
              <div className="rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-all hover:border-blue-400 hover:shadow-md">
                <div className="flex items-center gap-2 text-blue-600">
                  <metric.icon className="size-4" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{metric.label}</span>
                </div>
                <p className="mt-2 text-xl font-bold text-slate-900">{metric.value}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">{metric.hint}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

function ProductPreview() {
  return (
    <section id="preview" className="scroll-mt-20 py-20 border-t border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-5xl px-6">
        <Reveal className="text-center space-y-3">
          <Badge variant="outline" className="px-3 py-1 text-xs border-slate-300 bg-white">
            Interactive Output Preview
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">Transparent Clinical Intelligence</h2>
          <p className="mx-auto max-w-xl text-slate-600">
            Here is what a complete prediction result looks like in HealthIQ—combining risk gauge, confidence scores, clinical recommendations, and SHAP factor attributions.
          </p>
        </Reveal>

        <div className="mt-10 rounded-2xl border border-slate-200 bg-white shadow-xl overflow-hidden p-2 sm:p-6">
          <Suspense fallback={<Skeleton className="h-96 w-full rounded-xl" />}>
            <PredictionResult prediction={SAMPLE_PREDICTION} />
          </Suspense>
        </div>
      </div>
    </section>
  )
}

function BentoSection() {
  return (
    <section id="bento" className="scroll-mt-20 py-24 bg-white">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal className="text-center space-y-3 max-w-2xl mx-auto mb-16">
          <Badge variant="secondary" className="px-3 py-1 text-xs">
            Core Capabilities
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Engineered for Modern Clinical Systems
          </h2>
          <p className="text-slate-600">
            Built from the ground up to replace static scoring rules with explainable machine learning.
          </p>
        </Reveal>

        <BentoGrid>
          <BentoCard
            title="Real-Time Risk Calibration"
            description="Instant admission probabilities computed from vital signs, demographic data, and triage chief complaints."
            icon={Zap}
            badge="FastAPI Engine"
            className="md:col-span-2 border-slate-200 bg-slate-50/50"
          >
            <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 font-mono text-xs text-slate-600 shadow-xs">
              <div className="flex items-center justify-between text-slate-900 font-semibold mb-2">
                <span>POST /api/v1/predict</span>
                <span className="text-emerald-600 font-mono">200 OK · 14ms</span>
              </div>
              <p>{`{ "admission_probability": 0.78, "risk_category": "high", "confidence": 0.91 }`}</p>
            </div>
          </BentoCard>

          <BentoCard
            title="100% Explainable SHAP"
            description="Every prediction details exact clinical factor weights (+risk vs -risk)."
            icon={Lightbulb}
            badge="Explainable AI"
            className="border-slate-200 bg-slate-50/50"
          />

          <BentoCard
            title="CDC NHAMCS Dataset"
            description="Trained on nationally representative U.S. Emergency Department visit records."
            icon={Database}
            badge="Validated"
            className="border-slate-200 bg-slate-50/50"
          />

          <BentoCard
            title="Enterprise Security & Audit"
            description="Complete historical tracking with zero identifiable PHI storage."
            icon={Lock}
            badge="HIPAA Compliant"
            className="md:col-span-2 border-slate-200 bg-slate-50/50"
          >
            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="outline" className="gap-1 bg-white border-slate-300">
                <ShieldCheck className="size-3 text-emerald-600" /> Audit Logged
              </Badge>
              <Badge variant="outline" className="gap-1 bg-white border-slate-300">
                <Lock className="size-3 text-blue-600" /> Zero-PHI Architecture
              </Badge>
              <Badge variant="outline" className="gap-1 bg-white border-slate-300">
                <Server className="size-3 text-indigo-600" /> Isolated Execution
              </Badge>
            </div>
          </BentoCard>
        </BentoGrid>
      </div>
    </section>
  )
}

function PatientJourney() {
  const steps = [
    {
      num: '01',
      icon: Stethoscope,
      title: 'Triage Data Collection',
      body: 'Nurse inputs age, vitals (BP, pulse, O2), arrival mode, and chief complaint at triage.',
    },
    {
      num: '02',
      icon: Cpu,
      title: 'Gradient Boosting Inference',
      body: 'LightGBM model processes non-linear interactions across clinical features in <20ms.',
    },
    {
      num: '03',
      icon: Sparkles,
      title: 'SHAP Feature Attribution',
      body: 'TreeSHAP calculates exact marginal contributions for every single input feature.',
    },
    {
      num: '04',
      icon: UserCheck,
      title: 'Clinical Decision Support',
      body: 'Physician reviews probability gauge alongside top positive and negative risk factors.',
    },
  ]

  return (
    <section id="journey" className="scroll-mt-20 py-24 border-t border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal className="text-center space-y-3 max-w-2xl mx-auto mb-16">
          <Badge variant="outline" className="bg-white border-slate-300">Clinical Workflow</Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">The Patient Triage Journey</h2>
          <p className="text-slate-600">From initial registration to explainable AI decision support.</p>
        </Reveal>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, idx) => (
            <Reveal key={step.num} delay={idx * 90}>
              <div className="relative h-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-blue-400 hover:shadow-md">
                <span className="text-3xl font-extrabold text-blue-200">{step.num}</span>
                <div className="mt-3 flex size-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  <step.icon className="size-5" />
                </div>
                <h3 className="mt-4 text-base font-semibold text-slate-900">{step.title}</h3>
                <p className="mt-2 text-xs leading-relaxed text-slate-600">{step.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

function ArchitectureSection() {
  return (
    <section id="architecture" className="scroll-mt-20 py-24 bg-white">
      <div className="mx-auto max-w-5xl px-6">
        <Reveal className="text-center space-y-3 max-w-2xl mx-auto mb-12">
          <Badge variant="secondary">System Architecture</Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">Model & Infrastructure Specs</h2>
          <p className="text-slate-600">Built for high reliability, low latency, and full auditability.</p>
        </Reveal>

        <div className="grid gap-6 md:grid-cols-2">
          <Reveal>
            <Card className="h-full border-slate-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg text-slate-900">
                  <Cpu className="size-5 text-blue-600" />
                  ML Ensemble & Training
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-slate-600">
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="font-medium text-slate-900">Algorithm</span>
                  <span>LightGBM Gradient Boosting</span>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="font-medium text-slate-900">Training Data</span>
                  <span>NHAMCS (CDC) ED Visits</span>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="font-medium text-slate-900">Validation</span>
                  <span>5-Fold Stratified Cross-Validation</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium text-slate-900">Explainability</span>
                  <span>TreeSHAP Exact Attribution</span>
                </div>
              </CardContent>
            </Card>
          </Reveal>

          <Reveal delay={100}>
            <Card className="h-full border-slate-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg text-slate-900">
                  <Server className="size-5 text-indigo-600" />
                  API & Web Service Architecture
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-slate-600">
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="font-medium text-slate-900">Backend Framework</span>
                  <span>FastAPI (Python 3.12)</span>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="font-medium text-slate-900">Frontend Stack</span>
                  <span>React 19 + Vite + Tailwind v4</span>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="font-medium text-slate-900">Database Layer</span>
                  <span>SQLite + SQLAlchemy + Alembic</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium text-slate-900">Design Primitives</span>
                  <span>shadcn/ui + Lucide + Recharts</span>
                </div>
              </CardContent>
            </Card>
          </Reveal>
        </div>
      </div>
    </section>
  )
}

function FaqSection() {
  const [openIdx, setOpenIdx] = useState(null)

  return (
    <section id="faq" className="scroll-mt-20 py-20 bg-slate-50 border-t border-slate-200">
      <div className="mx-auto max-w-3xl px-6">
        <Reveal className="text-center space-y-3 mb-12">
          <Badge variant="secondary">FAQ</Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">Frequently Asked Questions</h2>
        </Reveal>

        <div className="space-y-3">
          {FAQS.map((faq, idx) => (
            <Reveal key={faq.question} delay={idx * 60}>
              <Card className="border-slate-200 bg-white">
                <button
                  onClick={() => setOpenIdx(openIdx === idx ? null : idx)}
                  className="flex w-full items-center justify-between p-5 text-left font-semibold text-sm text-slate-900"
                >
                  <span>{faq.question}</span>
                  <ChevronDown className={`size-4 transition-transform duration-200 text-slate-500 ${openIdx === idx ? 'rotate-180' : ''}`} />
                </button>
                {openIdx === idx && (
                  <div className="px-5 pb-5 text-xs sm:text-sm text-slate-600 border-t border-slate-100 pt-3">
                    {faq.answer}
                  </div>
                )}
              </Card>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-900 text-slate-200 py-12">
      <div className="mx-auto max-w-6xl px-6 flex flex-col sm:flex-row justify-between gap-8">
        <div className="space-y-3 max-w-xs">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-md">
              <Activity className="size-4.5" />
            </div>
            <span className="text-base font-bold text-white">HealthIQ</span>
          </Link>
          <p className="text-xs text-slate-400 leading-relaxed">
            AI-powered Emergency Department admission prediction and SHAP explainability platform.
          </p>
        </div>

        <div className="flex flex-wrap gap-8 text-xs text-slate-400">
          <div className="space-y-2">
            <p className="font-semibold text-white uppercase tracking-wider text-[10px]">Platform</p>
            <Link to="/app" className="block hover:text-white">Executive Dashboard</Link>
            <Link to="/app/predict" className="block hover:text-white">Triage Prediction</Link>
            <Link to="/app/explainability" className="block hover:text-white">SHAP Studio</Link>
            <Link to="/app/history" className="block hover:text-white">Prediction Archive</Link>
          </div>

          <div className="space-y-2">
            <p className="font-semibold text-white uppercase tracking-wider text-[10px]">Resources</p>
            <a href="https://github.com" target="_blank" rel="noreferrer" className="flex items-center gap-1.5 hover:text-white">
              <GithubIcon className="size-3.5" /> GitHub Repository
            </a>
            <a href="#architecture" className="flex items-center gap-1.5 hover:text-white">
              <FileText className="size-3.5" /> Technical Paper
            </a>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6 mt-8 pt-6 border-t border-slate-800 text-center text-xs text-slate-500">
        &copy; {new Date().getFullYear()} HealthIQ Healthcare AI Platform. All rights reserved.
      </div>
    </footer>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 selection:bg-blue-100">
      <SiteHeader />
      <main>
        <Hero />
        <ProductPreview />
        <BentoSection />
        <PatientJourney />
        <ArchitectureSection />
        <FaqSection />
      </main>
      <Footer />
    </div>
  )
}
