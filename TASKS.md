# TASKS.md — HealthIQ Frontend Complete Redesign Roadmap

# Sprint 7 — Complete Frontend Product Redesign

Status: 🚧 In Progress  
Owner: Senior Product & Design Engineering Team  
Goal: Transform HealthIQ into an award-winning, enterprise-grade, portfolio-worthy Healthcare AI Platform inspired by top-tier product design standards (Vercel, Stripe, Linear, Raycast, OpenAI, Apple).

---

# Implementation Roadmap

## Phase 1 — Comprehensive Design System & Foundation Tokens
- [ ] **Objectives**: Establish a unified, accessible, and expandable design token system supporting both Light and Dark modes with zero ad-hoc styling.
- [ ] **Checklist**:
  - [ ] Define complete color system: Clinical Blue (`oklch(0.47 0.16 258)`), Indigo, Teal, Emerald, Slate, Neutral Grays, Accent gradients.
  - [ ] Configure Dark Mode tokens (`.dark` class overrides in `index.css`) with rich contrast.
  - [ ] Extend typography system with Geist Variable font pairing, responsive scale (`--text-xs` to `--text-4xl`), and negative letter-spacing for headers.
  - [ ] Define shadow & depth scale (`shadow-xs`, `shadow-sm`, `shadow-md`, `shadow-lg`, `shadow-xl`, glassmorphic backdrops).
  - [ ] Define radius scale (`--radius` base, sm, md, lg, xl, 2xl, full).
  - [ ] Define custom easing curves (`--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`, `--ease-in-out`, `--ease-drawer`).
  - [ ] Create foundation UI components in `src/components/ui/` (`Button`, `Card`, `Badge`, `Input`, `Select`, `Tabs`, `Table`, `Skeleton`, `Dialog`, `Sheet`, `Tooltip`, `ToggleGroup`, `Separator`, `Command`, `Drawer`).
- [ ] **Dependencies**: `lucide-react`, `@fontsource-variable/geist`, `tw-animate-css`, `clsx`, `tailwind-merge`.
- [ ] **Reusable Components**: `Button`, `Card`, `Badge`, `GlassCard`, `GradientButton`, `ThemeToggle`.
- [ ] **Completion Criteria**: 100% of pages consume semantic tokens; zero raw Tailwind hex colors; zero unstyled native controls.

---

## Phase 2 — Landing Page Experience
- [ ] **Objectives**: Build a captivating, high-conversion, presentation-ready Landing Page showcasing HealthIQ's value proposition, AI capability, and clinical research foundation.
- [ ] **Checklist**:
  - [ ] **Hero Section**: Animated background grid, glowing radial gradients, headline typography, CTA button group, animated statistic pills.
  - [ ] **AI Prediction Interactive Illustration**: Live interactive mini-widget demonstrating immediate risk assessment.
  - [ ] **Interactive Dashboard Preview**: Layered card preview with hover tilt and depth.
  - [ ] **Hospital Analytics Preview**: Highlighting clinical throughput and admission rate monitoring.
  - [ ] **Feature Grid**: Bento-box layout detailing Real-time Inference, SHAP Explainability, Patient History, and EHR Integration.
  - [ ] **Interactive Patient Journey**: Step-by-step visual timeline from triage entry to explainable prediction.
  - [ ] **How Prediction Works & Model Architecture**: Interactive breakdown of NHAMCS dataset training, XGBoost/LightGBM ensemble, and SHAP computation.
  - [ ] **Clinical Workflow & Why Explainable AI Matters**: Medical trust, regulatory compliance, and physician decision support explanations.
  - [ ] **Research Highlights & Metrics**: Model AUC-ROC, accuracy, inference latency (<20ms), and validation parameters.
  - [ ] **Testimonials & Case Studies**: Fictional realistic clinical informatics quotes and hospital deployment statistics.
  - [ ] **FAQ Accordion**: Expandable answers to common questions about security, integration, and accuracy.
  - [ ] **Footer & Navigation**: Sticky header with blur, GitHub link, Research paper link, quick routes, and copyright.
- [ ] **Dependencies**: `lucide-react`, `recharts`, Framer Motion / CSS keyframe transitions.
- [ ] **Reusable Components**: `HeroSection`, `BentoGrid`, `FeatureCard`, `StatCounter`, `Timeline`, `InteractivePreview`, `FaqAccordion`.
- [ ] **Completion Criteria**: Pixel-perfect responsive landing page with reveal animations, zero layout shifts, and dark/light mode support.

---

## Phase 3 — Command & Analytics Dashboard
- [ ] **Objectives**: Transform the dashboard into an executive clinical intelligence panel with real-time stat tiles, trend charts, risk distributions, and recent activity.
- [ ] **Checklist**:
  - [ ] **KPI Stat Tiles**: Daily Admissions, Weekly Predictions Count, Model Health, System Latency, Database Status, High Risk Ratio.
  - [ ] **Admission Trends Chart**: Interactive Area Chart displaying daily vs. predicted triage volume over time.
  - [ ] **Risk Category Distribution**: Donut / Pie Chart showing Low, Moderate, and High risk patient breakdown.
  - [ ] **Confidence & Latency Monitor**: Line Chart tracking prediction confidence distribution over time.
  - [ ] **Hospital Utilization Heatmap**: Triage rush-hour matrix showing peak load times.
  - [ ] **Recent Patient Predictions Table**: Compact, interactive table with quick SHAP peek drawer.
  - [ ] **Quick Action Bar**: Pinned widgets for "New Patient Triage", "Export Daily Report", "Model Diagnostics".
  - [ ] **System & API Health Panel**: Live health status indicators with latency measurements.
- [ ] **Dependencies**: `recharts`, `PredictionsTable`, `StatTile`.
- [ ] **Reusable Components**: `StatTile`, `MetricCard`, `ChartCard`, `PredictionsTable`, `ActivityFeed`, `QuickActions`.
- [ ] **Completion Criteria**: Complete dashboard with dynamic chart rendering, responsive grids, loading skeletons, and empty states.

---

## Phase 4 — Redesigned Prediction Workflow & Patient Form
- [ ] **Objectives**: Replace the plain scrollable form with a modern multi-step / grouped wizard, live risk preview, and floating interactive prediction result panel.
- [ ] **Checklist**:
  - [ ] **Progressive Form Layout**: Two-column responsive layout (Form on left, Live Sticky Result Panel on right).
  - [ ] **Grouped Form Cards**: Demographics (`User`), Triage Vitals (`HeartPulse`), Complaints & Symptoms (`Activity`), Lab/Workup (`Microscope` - Collapsible).
  - [ ] **Enhanced Form Controls**: Custom styled sliders for Age/Vitals, segmented toggles for Binary inputs, search combobox for Primary Diagnosis.
  - [ ] **Live Validation & Auto-Formatting**: Real-time field validation, range helpers, tooltips with medical descriptions.
  - [ ] **Sticky Prediction Panel**:
    - [ ] **Initial State**: Helpful triage guidance and pre-filled quick-sample buttons.
    - [ ] **Predicted Outcome Gauge**: Animated circular probability ring / risk meter.
    - [ ] **Risk Badge & Clinical Recommendation**: High-visibility semantic badge with suggested clinical next steps.
    - [ ] **Top Contributor Summary**: Inline mini SHAP impact bars highlighting key positive/negative drivers.
- [ ] **Dependencies**: `PatientRecordFormConfig`, `PatientRecordAssembler`, `predictionApi`.
- [ ] **Reusable Components**: `ProbabilityGauge`, `RiskMeter`, `FormFieldGroup`, `PredictionResultCard`, `SampleRecordPicker`.
- [ ] **Completion Criteria**: Sub-second result feedback, zero scroll-jarring, responsive mobile stacking, fully accessible keyboard navigation.

---

## Phase 5 — Advanced SHAP Explainability Experience
- [ ] **Objectives**: Turn the Explainability page into a research-grade visual feature explorer with force plots, waterfall diagrams, dependence analyses, and feature rankings.
- [ ] **Checklist**:
  - [ ] **Interactive SHAP Waterfall / Diverging Bar Chart**: Color-coded feature contributions (+risk in red/destructive, -risk in emerald/success).
  - [ ] **Global Feature Importance Ranking**: Recharts bar chart displaying mean absolute SHAP values across dataset.
  - [ ] **Tabbed Analysis Modes**: "By Encoded Feature", "By Clinical Variable Group", "Feature Dependence & Correlation".
  - [ ] **Top Contributor Deep-Dive**: Filterable cards detailing Positive Contributors (Risk Drivers) vs Negative Contributors (Protective Factors).
  - [ ] **Synthesized Clinical Insight Generator**: Automated plain-language narrative summarizing top 3 decision factors.
  - [ ] **Interactive Feature Explorer**: Searchable list of all 18 features with mean importance, normal range, and weight.
  - [ ] **Export & Report Generator**: Download SHAP summary as PDF / PNG report.
- [ ] **Dependencies**: `GlobalImportanceChart`, `FeatureContributionChart`, `explanationService`.
- [ ] **Reusable Components**: `ShapWaterfall`, `FeatureRankingCard`, `InsightCallout`, `FeatureExplorerTable`.
- [ ] **Completion Criteria**: Interactive hover tooltips, smooth tab transitions, complete scientific documentation links.

---

## Phase 6 — Prediction History & Data Management
- [ ] **Objectives**: Build a high-performance, filterable, sortable prediction archive with data export and detail inspection drawer.
- [ ] **Checklist**:
  - [ ] **Advanced Data Table**: Header sorting, multi-column filters, search by ID / Risk level, pagination / page size controls.
  - [ ] **Dual View Modes**: Table View vs Timeline Card View.
  - [ ] **Expanded Row Detail**: Slide-out drawer or expandable row showing full patient vitals and top 6 SHAP factors.
  - [ ] **Export Capabilities**: Export history to CSV or JSON format.
  - [ ] **Historical Analytics Header**: Summary metrics of total predictions, average admission risk, and model uptime.
  - [ ] **Date Range Filter**: Filter historical records by date / session.
- [ ] **Dependencies**: `historyApi`, `predictionListUtils`.
- [ ] **Reusable Components**: `PredictionsTable`, `HistoryDetailDrawer`, `HistoryFilterBar`, `ExportButton`.
- [ ] **Completion Criteria**: Instant client-side sorting and filtering, clear empty states, responsive mobile card view fallback.

---

## Phase 7 — Comprehensive Charting & Data Visualization Suite
- [ ] **Objectives**: Standardize all chart components into a high-craft visual library matching the app's theme.
- [ ] **Checklist**:
  - [ ] Re-theme Recharts components using semantic CSS variables (`var(--primary)`, `var(--destructive)`, `var(--success)`, `var(--muted-foreground)`).
  - [ ] Custom tooltip components with glassmorphism backgrounds and precise alignment.
  - [ ] Responsive container wrapper ensuring zero chart clipping on mobile.
  - [ ] Smooth entrance animations for bar charts, area fills, and line nodes.
- [ ] **Dependencies**: `recharts`.
- [ ] **Reusable Components**: `CustomChartTooltip`, `ChartContainer`, `DivergingBarChart`, `AreaTrendChart`, `DonutChart`.
- [ ] **Completion Criteria**: Fully themed, high contrast, zero render errors, zero layout shifts.

---

## Phase 8 — Motion, Micro-interactions & Design Engineering Polish
- [ ] **Objectives**: Implement Emil Kowalski's design engineering principles across every interactive element.
- [ ] **Checklist**:
  - [ ] Add `:active { transform: scale(0.97); }` press feedback to all buttons and interactive cards.
  - [ ] Never animate from `scale(0)`; use `scale(0.95)` + `opacity: 0` with custom `--ease-out` curve (`cubic-bezier(0.23, 1, 0.32, 1)`).
  - [ ] Apply origin-aware popover and dropdown entrances.
  - [ ] Stagger entrance delays (30-80ms) for grid cards and list items.
  - [ ] Add loading shimmer / skeleton placeholders for all async data states.
  - [ ] Add subtle hover glow effects (`group-hover:shadow-md`, subtle border highlights).
- [ ] **Dependencies**: `tw-animate-css`, `emil-design-eng` skill rules.
- [ ] **Reusable Components**: `Reveal`, `ShimmerLoader`, `MotionCard`, `AnimatedCounter`.
- [ ] **Completion Criteria**: Every interactive element gives instant tactile feedback under 200ms; zero sluggish transitions.

---

## Phase 9 — Accessibility, Mobile Responsiveness & Keyboard Navigation
- [ ] **Objectives**: Guarantee universal access and flawless layout across all screen sizes.
- [ ] **Checklist**:
  - [ ] Ensure 100% keyboard accessibility: focus rings (`focus-visible:ring-2`), logical tab order, ESC to close drawers/modals.
  - [ ] Complete ARIA attributes across all custom components (`aria-expanded`, `aria-selected`, `aria-live`, `role`).
  - [ ] Enforce contrast ratios exceeding WCAG AA standards in both Light and Dark modes.
  - [ ] Test layout across viewport widths: 320px (Mobile S), 375px (Mobile M), 768px (Tablet), 1024px (Laptop), 1440px (Desktop), 2560px (Ultrawide).
  - [ ] Implement responsive left sidebar drawer (`Sheet`) for mobile screens.
- [ ] **Dependencies**: Radix primitives, `@media (hover: hover) and (pointer: fine)`.
- [ ] **Completion Criteria**: Pass all automated accessibility audits; zero horizontal scrollbars on mobile.

---

## Phase 10 — Performance Optimization, Code Quality & Handoff
- [ ] **Objectives**: Optimize bundle size, eliminate unnecessary re-renders, and format code to production standards.
- [ ] **Checklist**:
  - [ ] Code splitting with `React.lazy()` for all heavy routes and Recharts components.
  - [ ] Tree-shake icon imports from `lucide-react`.
  - [ ] Memoize expensive computations and chart data transformations (`useMemo`, `useCallback`).
  - [ ] Verify production build (`npm run build`) generates optimized chunks with zero warnings.
  - [ ] Run full test suite (`npm run test`) to ensure 100% test passing rate.
  - [ ] Generate final walkthrough artifact documenting the entire redesign.
- [ ] **Dependencies**: `vite`, `vitest`.
- [ ] **Reusable Components**: All system components.
- [ ] **Completion Criteria**: Sub-500KB initial chunk size, 100% passing tests, zero console warnings.
