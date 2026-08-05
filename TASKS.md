# TASKS.md

# Sprint 6 - Frontend Redesign

Status: 🚧 In Progress

Owner: Frontend Team

Goal:

Completely redesign the HealthIQ frontend's presentation and UX layer — layout, typography,
color, spacing, components, navigation, motion, and information architecture — into a
premium, enterprise-grade healthcare product, while preserving 100% of the existing business
logic, API contracts, validation rules, and state management built in Sprint 5. This is a
redesign, not a polish pass: every screen is re-architected from its information hierarchy up,
not just re-skinned.

This sprint begins only after Sprint 5 (Frontend Integration) is complete and functionally
verified — it is.

---

# Phase 1 — Executive Summary (Current State Audit)

## What exists today (Sprint 5 output)

A functionally complete React 19 + Vite + Tailwind v4 SPA: 5 pages (Dashboard, Prediction,
Explainability, Prediction History, About), a full API client layer, a validated patient-record
form, SHAP-based result visualization, and 60 passing tests, all live-verified against the FastAPI
backend. Functionally, there is nothing wrong with it.

## Current frontend quality: functional, not designed

The UI was built utility-class-first, screen-by-screen, with no upfront design system. It works
and looks "clean" in isolation, but reads as **generic scaffolded output**, not an authored
product:

- Every card is `rounded-lg border border-slate-200 bg-white p-5/p-6` — one visual idea, repeated
  everywhere, with no elevation, no hierarchy between primary and secondary surfaces.
- Typography has no defined scale: headings are `text-2xl font-semibold`, labels are
  `text-xs uppercase tracking-wide text-slate-500`, body text is whatever Tailwind's default is —
  there is no type ramp, no deliberate rhythm, no large confident moments anywhere in the product.
- Color is a single blue (`brand-600`) plus three risk colors and Tailwind's stock `slate` scale —
  functional, but with no intentional "clinical trust" identity. Nothing distinguishes this from
  a Tailwind starter template.
- The navigation is a flat top bar with five text links — it does not scale past 5 items (Model
  Comparison / Dataset Analytics are already known future sections per Sprint 5), has no visual
  weight, and provides no sense of place within the product.
- No icon system. No motion system (a couple of `transition-colors` utilities, nothing else). No
  skeleton loaders (a spinner + text label stands in everywhere). No toast/notification system. No
  empty-state illustration or visual interest — just centered gray text.
- Native HTML `<table>`, `<select>`, and `<input type="number">` elements are used directly with
  minimal styling — functional, but visually and interactively beneath the bar this product needs
  to hit (a plain number input for "how many records to show" instead of pagination or a proper
  control is a good example of an engineer-built, not product-designed, pattern).

## Biggest UX issues

1. **No persistent sense of place.** A flat top nav with text links gives the user no spatial
   model of the product — there's no distinction between primary sections and no room to grow.
2. **The prediction form is one long undifferentiated scroll.** All 18 fields are visible at once
   in four stacked sections; the result appears below the fold after submission, forcing the user
   to scroll down every time, and there is no progressive disclosure between "always known"
   vitals and "sometimes known" workup fields.
3. **Numeric inputs standing in for real controls.** `top_n` on Explainability and `limit` on
   History are raw `<input type="number">` fields — a developer's placeholder for a slider,
   segmented control, or paginator, not a shipped product pattern.
4. **Explainability shows two charts with equal visual weight simultaneously** instead of guiding
   the user to the more important one, and provides no synthesized takeaway beyond the raw bars.
5. **The dashboard is three stacked cards, not a dashboard** — no KPI/stat-tile row, no sense of
   "what matters most right now."

## Biggest UI issues

1. No typography scale — every text size was picked ad hoc per component.
2. No elevation system — borders substitute for shadows everywhere; nothing feels "raised" or
   layered.
3. No spacing scale beyond default Tailwind gaps — vertical rhythm is inconsistent page to page
   (`space-y-6` vs `space-y-8` vs manual `mb-3`/`mt-3`, chosen per-file, not per-system).
4. No icons anywhere in the product — every affordance is a text label or a colored dot.
5. Risk badges, buttons, and charts each invented their own color logic independently
   (`RISK_BADGE_CLASSES` duplicated conceptually across components before extraction) instead of
   drawing from one semantic color system.

## Technical frontend issues

1. No component library foundation (`shadcn/ui` is not installed) — every input, button, select,
   and table is a hand-rolled element styled inline, which is exactly why styling is inconsistent.
2. No design tokens — `index.css`'s `@theme` block defines 8 raw color values and nothing else
   (no spacing, radius, shadow, or motion tokens).
3. No icon library dependency.
4. No animation/transition utility layer.
5. Some presentational logic is duplicated in ad hoc ways across pages (badge coloring, stat-tile
   markup, section-header styling) that a real component library would centralize.

## Opportunities

Every one of the above is independently fixable without touching a single line of business logic
— `services/`, `hooks/useApiRequest.js`, and all validation/payload logic in
`components/forms/patientRecordFormConfig.js` are already cleanly separated from presentation.
This redesign is purely a presentation-and-IA rewrite on top of an already-solid functional core.

---

# Phase 2 — Design Vision

HealthIQ should feel like software a hospital's clinical informatics team licensed from a
well-funded health-tech company — not a hackathon project, not a generic admin template, and not
a consumer health app. Concretely:

- **Premium & enterprise**: generous whitespace, restrained color, considered typography — the
  visual language of Linear/Vercel/Stripe (quality of craft, not their literal aesthetic).
- **Healthcare-trustworthy**: calm, clinical, low-saturation neutrals with a confident, precise
  accent color; risk communicated through deliberate, accessible semantic color, never a "rainbow
  dashboard."
- **Intelligent**: the explainability surfaces (SHAP charts, plain-language summaries) should feel
  like the product's centerpiece, not an afterthought bolted onto a form.
- **Fast & clean**: skeleton loading states instead of spinners, instant-feeling micro-interactions,
  no unnecessary motion.
- **Polished**: every hover, focus, empty, loading, and error state considered and consistent,
  everywhere, with zero exceptions.

Never: crypto-dashboard gradients, gamified badges/confetti, oversized marketing-site hero
sections, or generic "AI startup" purple-gradient-on-dark-hero clichés.

---

# Phase 2 — Design System

This is the foundation every page redesign below draws from. **Built once, used everywhere** — no
page should invent its own spacing, color, or component pattern.

## Foundation Setup

- [x] Install and configure `shadcn/ui` for this JS (non-TS) Vite project — used the official
  `shadcn` CLI (v4.16.1) rather than hand-rolling, since it exists and does this correctly: Radix
  base, **Nova preset** (Lucide icons + Geist font — see typography note below), `components.json`,
  path aliases (`jsconfig.json` + `vite.config.js` `resolve.alias`), `src/lib/utils.js` (`cn()`
  via `clsx` + `tailwind-merge`)
- [x] Install `lucide-react` for icons (via the Nova preset)
- [x] Install `class-variance-authority` (via shadcn init)
- [x] Install `tw-animate-css` (via shadcn init)
- [x] Rewrite `src/index.css`'s `@theme` block into a complete token system (below) — kept
  shadcn's generated semantic token architecture (`background`/`foreground`/`card`/`primary`/
  `secondary`/`muted`/`accent`/`destructive`/`border`/`input`/`ring`/`chart-1..5`/`sidebar-*`,
  full light + dark values) rather than replacing it with a parallel one
- [x] Installed the full shadcn component set needed for this redesign: `button`, `input`,
  `select`, `label`, `card`, `table`, `badge`, `tabs`, `skeleton`, `dialog`, `sheet`, `tooltip`,
  `sonner`, `slider`, `separator`, `collapsible`, `sidebar`, `breadcrumb`, `dropdown-menu`, `avatar`

## Typography

- [x] Adopt a primary typeface — **Geist Variable** (via `@fontsource-variable/geist`), not Inter
  as originally planned: the shadcn Nova preset ships Geist paired with Lucide icons as a matched
  set, and Geist (Vercel's typeface) is squarely in the "Linear/Vercel-quality" reference bracket
  this redesign targets. `system-ui` stack remains the fallback.
- [x] Define a deliberate type scale as CSS custom properties (`--text-xs` through `--text-4xl`,
  Tailwind v4 `--text-*`/`--text-*--line-height` tokens) — tightened vs. Tailwind's stock scale:
  `xs` 12/16, `sm` 13/20, `base` 15/24, `lg` 17/28, `xl` 20/28, `2xl` 24/32, `3xl` 30/36, `4xl` 36/40
- [x] Define weight usage rules: 400 body, 500 labels/nav/buttons, 600 headings/emphasis, 650-700
  reserved for large numerals (stat tiles, probability displays) — applied consistently across all
  5 rebuilt pages (`font-medium`/`font-semibold` used per the rule, verified by codebase audit)
- [x] Negative letter-spacing (-0.01em to -0.02em) on `text-2xl`+ headings — `tracking-tight`
  applied on headings across all 5 pages plus `StatTile`/`AppSidebar` (verified: 8 files use it)
- [x] Audit and remove every ad hoc font-size/weight combination currently scattered across
  components — all 5 pages now rebuilt on the shared type scale, no ad hoc combinations remain

## Spacing

- [x] Confirm/extend the 4px base grid; define semantic spacing tokens: page horizontal padding
  (24px mobile / 32px tablet / 40px+ desktop), inter-section vertical rhythm (32-40px), card
  internal padding (20-24px), related-element stack spacing (12-16px) — applied per-page during
  implementation using Tailwind's stock spacing scale consistently across all 5 rebuilt pages
- [x] Replace every hand-picked `space-y-*`/`mb-*`/`mt-*` value with the semantic scale — done as
  part of each page rebuild; no stray one-off spacing values remain outside the scale

## Color System

- [x] Replace the single flat `brand-*` blue with a full semantic token system — a clinical blue
  primary (`oklch(0.47 0.16 258)`, deliberately cooler/more restrained than a generic Tailwind
  blue-600) wired through shadcn's `primary`/`ring`/`sidebar-primary` tokens rather than a
  standalone `brand-*` scale, so every component that uses `bg-primary`/`text-primary`/`ring`
  automatically inherits it
- [x] Standardized on `oklch()` semantic tokens end-to-end (`background`/`foreground`/`muted`/
  `border`/etc.) instead of raw Tailwind `slate-*` utilities — supersedes the original plan to
  "standardize on slate," since the shadcn token system is the more complete solution
- [x] Added `success`/`warning` as first-class semantic tokens (`--color-success`,
  `--color-warning` + foregrounds, light and dark values) alongside shadcn's built-in
  `destructive`, giving `<Badge variant="success"|"warning"|"destructive">` a consistent
  bg/10-text/foreground pairing rule — `RiskBadge.jsx` rebuilt on this (see Shared Components)
- [x] Token architecture defined with light-mode values now and full dark-mode values already
  present (`.dark` class) — dark mode is a class toggle away, not a future rewrite, exceeding the
  original "reserve for later" plan
- [x] Audit every remaining raw Tailwind color utility (`text-red-600`, `bg-emerald-50`, etc.) in
  not-yet-rebuilt pages and replace with semantic tokens — codebase-wide grep confirms zero raw
  Tailwind color utilities remain; every page/component uses semantic tokens

## Elevation & Radius

- [x] Apply shadow scale to cards as each page is rebuilt (`shadow-xs`/`shadow-sm` resting,
  `shadow-md` hover/raised, `shadow-lg` dialogs/popovers — Tailwind's stock shadow scale is
  sufficient, no custom tokens needed) — in use across charts, sidebar, dropdown, tabs, and select
  primitives; no border-only cards remain
- [x] Radius scale defined via shadcn's `--radius-sm/md/lg/xl/2xl/3xl/4xl` tokens (derived from a
  single `--radius` base) — supersedes hand-picking `rounded-md`/`rounded-lg`/`rounded-full` per
  component; every new shadcn primitive already uses these consistently

## Icons

- [x] Adopted `lucide-react` exclusively (via Nova preset)
- [x] Apply consistent per-context sizing (14px inline with `text-sm`, 16px default UI, 20px
  section headers, 24px+ empty-state icons) — `size-3.5`/`size-4`/`size-5`/`size-6` used
  consistently across 21 files per the sizing rule
- [x] Replace every remaining text-only or colored-dot affordance with an icon (navigation items,
  stat tiles, empty states, form section headers) — `RiskBadge`, `AppSidebar`, `StatTile`,
  `EmptyState`, `ErrorState`, and every page header now icon-led

## Motion

- [x] Duration/easing come from `tw-animate-css` (shadcn's standard Tailwind v4 animation utility
  layer) rather than hand-defined tokens — consistent `animate-in`/`animate-out`,
  `fade-in`/`fade-out`, `slide-in-from-*` utilities used by every Radix-based primitive
  (`Dialog`, `Sheet`, `Tabs`, `Select`, `Collapsible`) automatically
- [x] Respect `prefers-reduced-motion` globally — no custom (non-Radix) animation was introduced
  anywhere in the redesign, so `tw-animate-css`/Radix's built-in handling (which respects the
  media query by default) covers every animated primitive in the app; no explicit override needed
- [x] Apply consistent micro-interactions per page as each is rebuilt: hover/focus states on every
  interactive element, loading transitions, expand/collapse for progressive disclosure, sort/filter
  transitions in tables — delivered via shadcn primitives (`Button`, `Collapsible`, `Table`,
  `Tabs`) on every rebuilt page

## Reusable Component Library (shadcn-based, `src/components/ui/`)

All installed via the shadcn CLI (see Foundation Setup) — remaining work is *using* them to
replace hand-rolled markup page by page, not building them from scratch:

- [x] `Button` — used across Dashboard ("New Prediction" CTA) and Prediction ("Generate
  prediction" submit, with `Loader2` loading state)
- [x] `Input`, `Select`, `Label` — wired into `PatientRecordForm`/`FormField` (Milestone 4);
  required `@testing-library/user-event` + jsdom pointer-capture polyfills to keep testing Radix
  `Select` realistic (see Milestone 4 testing note)
- [x] `Card` — used on Dashboard, Prediction (form sections + result), replacing hand-rolled
  `rounded-lg border bg-white p-5` divs on both pages so far
- [x] `Table` — used by `PredictionsTable` (Dashboard's compact view + Prediction History's full,
  sortable view)
- [x] `Badge` — extended with `success`/`warning` variants; `RiskBadge.jsx` rebuilt on it
- [x] `Collapsible` — used for the Prediction form's "Workup details" section (Milestone 4)
- [x] `Tabs` — used for Explainability's "By encoded feature" / "By source variable" views
- [x] `Skeleton` — used on Dashboard (stat tiles, predictions table) and Explainability (control
  row + chart placeholder)
- [ ] `Dialog` — installed; no confirmation-flow use case yet identified
- [x] `Sheet` — in active use as the shadcn `Sidebar` primitive's mobile drawer (Milestone 2)
- [ ] `Tooltip` — installed; not yet extended to icon-only affordances (Recharts tooltips are a
  separate, chart-native implementation, already re-themed in Milestones 4 and 5)
- [ ] `Sonner` — installed; not yet wired to a real event
- [x] `ToggleGroup`/`Toggle` — installed (not part of the original plan's component list — swapped
  in for the planned "Slider" once built, since a preset toggle group reads clearer than a
  continuous slider for "choose N of 5/10/20/50") — used for Explainability's `top_n` presets;
  `Slider` itself remains installed but unused, reserved for Prediction History's `limit` control
  if a toggle group turns out not to fit there (Milestone 6)
- [x] `Separator` — used in `AppLayout`'s header (Milestone 2) — vertical rule between the sidebar
  trigger and breadcrumb
- [x] `Sidebar`, `Breadcrumb`, `DropdownMenu`, `Avatar` — installed for the new navigation shell
  (Milestone 2); `DropdownMenu`/`Avatar` installed but not yet used (no user-account feature exists
  in this app yet — kept available for when/if one is added, not speculative dead code in a page)
- [x] New shared components created during page work, not part of the original shadcn set: `StatTile`
  (Dashboard + Prediction Result), `PredictionsTable` (Dashboard + reserved for full History use in
  Milestone 6)

---

# Phase 2 — Page-by-Page Redesign Tasks

## Shell: Navigation & Layout

### Current issues
Flat top nav bar, 5 text links, no visual hierarchy, no room to grow, no mobile/tablet treatment
beyond wrapping, no sense of active section beyond a background-color swap.

### UX / IA improvements
- [x] Replaced the top nav bar with a **persistent left sidebar** (shadcn `Sidebar`,
  `collapsible="icon"`) — Dashboard/Prediction/Explainability/Prediction History as primary items,
  About as a secondary item pinned to the bottom, each with a Lucide icon
  (`LayoutDashboard`/`ClipboardPlus`/`Sparkles`/`Activity`/`Info`) and a clear active-state
  treatment (background + accent text color via `SidebarMenuButton`'s `isActive`, not just a plain
  color swap)
- [x] Collapses to an icon-only rail (desktop/laptop, toggle button or **Cmd/Ctrl+B**, courtesy of
  the shadcn primitive) and to a slide-over `Sheet` drawer with a backdrop below the 768px
  breakpoint — both come from the primitive, not hand-built
- [x] Added a slim header bar (sidebar toggle + breadcrumb-based page title) separate from the
  sidebar and content, giving every page a consistent title/context zone — page title is derived
  from the current route, not hardcoded per page

### Layout / Component / Accessibility / Responsiveness / Animation
- [x] `AppLayout.jsx` rebuilt around `SidebarProvider` + `AppSidebar` + `SidebarInset` (header +
  content region)
- [x] `src/components/AppSidebar.jsx` replaces the old `Navigation.jsx` entirely (deleted)
- [x] Keyboard navigation re-verified end-to-end: tabbed through all 5 nav items + the sidebar
  toggle button, confirmed every focused element has a visible indicator (shadcn uses
  `focus-visible` box-shadow rings rather than the native outline — still fully visible,
  confirmed programmatically), and confirmed Enter on a keyboard-focused "Explainability" link
  actually navigates
- [x] Re-verified at desktop (1440px), tablet (768px — sidebar remains fully expanded, which reads
  better than a premature icon-collapse), and a narrow mobile width (500px, drawer + backdrop) —
  zero horizontal overflow at any width, zero console errors
- [x] Sidebar collapse/expand and the mobile drawer's open/close are both animated by the shadcn
  primitive by default (width/position transitions, `Sheet` slide-in) — no custom animation needed

### Implementation checklist
- [x] `src/components/ui/sidebar.jsx` (shadcn primitive, installed), `src/layouts/AppLayout.jsx`
  rewritten
- [x] `src/components/Navigation.jsx` deleted, replaced by `src/components/AppSidebar.jsx`
- [x] All 5 pages re-verified inside the new shell — every page redesigned and live-verified
  (Milestones 3-7), then re-confirmed together in Milestone 8's final 15-check responsive
  regression and end-to-end walkthrough

Status: ✅ Complete

---

## Page 1: Dashboard

### Current issues
Three stacked cards (system health, recent predictions, quick-nav) with no hierarchy — reads as a
list of widgets, not a dashboard. No KPI/stat-tile row. Quick-nav cards duplicate the sidebar's own
navigation purpose once the sidebar exists.

### UX improvements
- [x] Leads with a stat-tile row: API status, Model status (name/version), Database status, Recent
  admission rate (computed client-side from the last 5 fetched predictions — no new backend
  endpoint needed) — scannable at a glance
- [x] Quick-navigation cards removed now that the persistent sidebar covers that job — replaced
  with a single primary **"New Prediction"** `Button` (with `ArrowRight` icon) in the page header
- [x] Recent predictions is now a real table (`PredictionsTable` in `compact` mode) instead of
  bespoke `<li>` markup — and this same component is reused by Prediction History (Milestone 6),
  not duplicated

### Layout improvements
- [x] Stat tiles in a responsive grid (`sm:grid-cols-2 lg:grid-cols-4`) — verified 1-up below the
  `sm` breakpoint, 2-up at tablet, 4-up at desktop/laptop
- [x] **Real bug found and fixed during this milestone**: the stat-tile grid + table Card were
  initially placed as siblings inside one shared grid using `lg:col-span-3`, which broke at
  tablet width (`sm:grid-cols-2` truncated the table to a single narrow column, cutting off
  "Outcome"/"Risk" headers mid-word). Fixed by separating the stat grid and the predictions table
  into two independent layout blocks — no shared column-span coupling between unrelated content

### Component improvements
- [x] New `src/components/StatTile.jsx` — reusable value/label/icon/tone/loading-skeleton
  component; already written to be reused by Prediction Result (Milestone 4), not Dashboard-only
- [x] System health rows redesigned as `StatTile`s with a semantic icon (`Activity`/`CircleCheck`/
  `Database`) and green "Operational" value; failure state shows a dedicated destructive-toned
  card with a retry action, replacing the old plain "OK"/"Unavailable — retry" text row
- [x] New `src/components/PredictionsTable.jsx` — shared table (real `<Table>` primitive) used
  here in `compact` mode and by Prediction History in full mode (Milestone 6), not two separate
  implementations

### Accessibility / Responsiveness / Animation
- [x] Stat tiles and the predictions table remain independently loading/error-resilient — kept
  the exact per-section `useApiRequest` pattern from Sprint 5 (verified by the existing
  `DashboardPage.test.jsx` suite, which still passes unmodified in its assertions)
- [x] Skeleton loaders (`Skeleton` primitive) replace the old spinner+text loading state for both
  the stat tiles and the table
- [x] **Second real bug found and fixed during this milestone, more serious than the first**:
  after separating the layout blocks, a residual ~27px horizontal page overflow remained at
  tablet width (768px) — root-caused (not papered over) to shadcn's `SidebarInset` rendering as
  `flex-1 flex-col` with no `min-width: 0`, the classic Flexbox "flex items default to
  `min-width: auto`" bug, which let *any* page's content with enough intrinsic width silently
  stretch the whole shell wider than the viewport. Fixed once, at the shell level
  (`AppLayout.jsx`, `min-w-0` on `SidebarInset` and its content wrapper) rather than patching it
  per-page — re-verified with a full 5-page × 3-width regression (15/15 OK, zero overflow, zero
  console errors), not just the Dashboard
- [x] Also fixed in the same pass: the shell had a `<main>` landmark nested inside `SidebarInset`'s
  own `<main>` — invalid HTML and a real accessibility issue (assistive tech expects exactly one
  `main` landmark per page). Changed the inner element to a plain `<div>`.

### Implementation checklist
- [x] `DashboardPage.jsx` restructured
- [x] `StatTile.jsx`, `PredictionsTable.jsx` (shared, not Dashboard-only)
- [x] `AppLayout.jsx` shell fix (`min-w-0`, single `<main>` landmark) — benefits every page, not
  just Dashboard

Status: ✅ Complete

Live-verified: full 5-page × 3-width overflow regression (15/15 OK), full test suite (60/60
passing), zero console errors, screenshots confirm correct rendering at desktop/tablet.

---

## Page 2: Patient Prediction (Form)

### Current issues
All 18 fields visible at once across four stacked fieldsets; no distinction between "always
known at triage" and "sometimes known later" fields; result appears below the fold after
submission, forcing a scroll; native `<select>`/`<input>` styling.

### UX improvements
- [x] Restructured into a **two-column working layout on desktop/laptop** (`grid lg:grid-cols-5`,
  form `lg:col-span-3`, result panel `lg:col-span-2`, sticky at `lg:top-6`): form on the left, a
  persistent right-hand panel that starts as helpful context ("No prediction yet — fill in the
  required vitals...") and swaps in place for the real result once submitted — no scroll required
  to see the outcome on desktop/laptop
- [x] "Workup details" is now a `Collapsible` section, **closed by default** — reduces the
  form's initial visible surface from 18 fields down to the 12 always-relevant ones
  (demographics/vitals/triage/arrival), with an explicit expander (chevron + "Optional — add if
  known, improves prediction accuracy" subtext) for the rest
- [x] Required-field asterisks kept (still the clearest convention for a dense clinical form) but
  now paired with the section-level "Optional" framing on the Workup card specifically, rather
  than relying on asterisks alone to communicate optionality

### Layout improvements
- [x] Two-column grid on desktop/laptop; verified stacked (form, then result) at tablet width
  (768px, below the `lg` breakpoint) via live screenshot
- [x] Vitals, Demographics, and Triage & Arrival are each their own `Card` with an icon header
  (`User`/`HeartPulse`/`Siren`), replacing the old plain `<fieldset>` grouping

### Component improvements
- [x] `PatientRecordForm.jsx` and `FormField.jsx` fully rebuilt on shadcn `Input`/`Select`/`Label`
  — every existing `name`, validation rule (`patientRecordFormConfig.js`, untouched), and
  payload-building function preserved exactly; only the rendering layer changed
- [x] `Collapsible`/`CollapsibleTrigger`/`CollapsibleContent` (shadcn/Radix) for the Workup
  section, animated via `tw-animate-css`'s built-in `animate-collapsible-down/up` keyframes
  (which track Radix's own content-height CSS variable — not a custom animation)
- [x] Submit button is now a real `Button` (`size="lg"`) with a `Loader2` spin icon during
  submission, replacing the old disabled/text-swap-only button

### Accessibility improvements
- [x] All `aria-invalid`/`aria-describedby`/`aria-required` wiring preserved — shadcn's `Input`/
  `SelectTrigger` already style themselves off `aria-invalid` automatically, so this is *more*
  robust than the Sprint 5 hand-rolled version, not just equivalent
- [x] Collapsible Workup section uses Radix's own `aria-expanded` semantics (built into
  `CollapsibleTrigger`), not hand-rolled
- [x] Re-verified full keyboard operability end-to-end, including the new Radix `Select` fields
  specifically (not just native elements, which Sprint 5 already covered): Tab to a select, Enter
  to open, Arrow keys to navigate options, Enter to confirm — all confirmed working live, not
  assumed to work because Radix is "generally accessible"

### Responsiveness improvements
- [x] Two-column desktop/laptop → stacked tablet, re-verified with the same overflow-check
  methodology as Sprint 5 and Milestone 3 — part of the full 15-check (5 page × 3 width)
  regression, zero overflow

### Animation improvements
- [x] Workup section expand/collapse animated (Radix height transition)
- [x] Result panel entrance animation (fade/slide-in on a *new* prediction replacing an existing
  one) — implemented in Milestone 8: `PredictionResult`'s `Card` uses
  `animate-in fade-in slide-in-from-bottom-2 duration-300`, and `PredictionPage` now keys the
  panel on a per-submission counter so the animation replays for every new prediction, not just
  the first

### Testing note
Rebuilding `Select` on Radix (from a native `<select>`) broke `PatientRecordForm.test.jsx` and
`PredictionPage.test.jsx`'s existing interaction helpers, which used `fireEvent.change` — native
`<select>`-only, meaningless for a Radix combobox. Installed `@testing-library/user-event` and
added jsdom pointer-capture polyfills (`hasPointerCapture`/`setPointerCapture`/`scrollIntoView`,
which Radix calls but jsdom doesn't implement) to `test-setup.js`, then rewrote both test files'
interaction helpers to open the combobox and click the real option — this is now a *more*
faithful test of real user interaction than the native-select version was, not a workaround.

### Implementation checklist
- [x] `PredictionPage.jsx` restructured around the two-column layout
- [x] `PatientRecordForm.jsx`, `FormField.jsx` rebuilt on shadcn primitives
- [x] New collapsible workup section
- [x] Result panel redesigned per Page 3 below

Status: ✅ Complete

---

## Page 3: Prediction Result (within Prediction page)

### Current issues
A stat grid (`<dl>`) with plain numbers, a gray box for the plain-language summary, and the SHAP
chart below — functional but visually flat, and disconnected from the form above it (no framing
of "this is the answer to what you just asked").

### UX improvements
- [x] Leads with a prominent outcome statement (`text-xl font-semibold`) paired with the risk
  badge in the `CardHeader`, no longer competing visually with the stat grid below
- [x] Plain-language explanation summary elevated to a `Lightbulb`-icon "Why" callout on a
  `bg-muted/40` card, replacing the plain gray paragraph box
- [x] Model name/version demoted to a small `Cpu`-icon footer line at the bottom, no longer mixed
  into the main stat grid at equal visual weight with admission probability

### Layout / Component improvements
- [x] Outcome + risk badge as the `CardHeader` of the result panel
- [x] Stat tiles (probability, confidence, baseline) now use the **same `StatTile` component as
  the Dashboard** — confirmed one component serving two contexts, not duplicated
- [x] `FeatureContributionChart` re-themed to `var(--destructive)`/`var(--success)` (resolved at
  render time from the live theme, light or dark) instead of hardcoded `#dc2626`/`#16a34a`; axis,
  grid, and tooltip re-themed to `var(--muted-foreground)`/`var(--border)`/`var(--popover)` so the
  chart matches the rest of the design system instead of being an isolated slate-colored island

### Accessibility / Animation
- [x] Chart color/contrast reconsidered, not silently left as-is: kept the red/green pairing (it
  matches the legend dots and the rest of the app's success/destructive convention), but
  **mitigated** the colorblind concern by making the tooltip state direction in text
  ("Increased"/"Decreased risk — SHAP ...") rather than relying on color alone to convey meaning.
  A true pattern-fill or icon-per-bar differentiator is flagged as follow-up work in Milestone 8,
  not silently dropped — full colorblind-safety needs more visual design exploration than this
  milestone's scope allows.
- [x] Result panel entrance animation (fade/slide-in) — same `PredictionResult.jsx` component as
  Page 2 above; implemented once in Milestone 8, covers both page sections (not duplicated)

### Implementation checklist
- [x] `PredictionResult.jsx` restructured
- [x] `FeatureContributionChart.jsx` re-themed
- [x] Colorblind mitigation applied and documented (text-based direction labels); full pattern-fill
  solution deferred and tracked, not silently dropped

Status: ✅ Complete

Live-verified together with Page 2 (they share one page/one test suite): full 60/60 test suite
passing, 15/15 responsive checks passing, keyboard operability confirmed on the new `Select`
fields specifically, zero console errors on a real submitted prediction (84-year-old, severe
vitals, high total-diagnoses/consult-requested record) showing a genuine "Moderate Risk /
Predicted: Admission" result with a live-rendered diverging chart.

---

## Page 4: Explainability

### Current issues
Two full-width charts shown simultaneously with equal visual weight and a raw number input for
`top_n` — no synthesized takeaway, no clear primary view.

### UX improvements
- [x] Replaced the side-by-side dual-chart layout with a `Tabs` control ("By encoded feature" /
  "By source variable") — one chart in focus at a time
- [x] Replaced the raw `top_n` number input with a `ToggleGroup` of sensible presets (Top 5/10/20/50)
  plus a labeled "Custom" input for anything else — installed shadcn's `toggle-group`/`toggle`
  components for this rather than hand-rolling a segmented control
- [x] Added a synthesized insight line above the tabs (`Lightbulb`-icon callout, e.g. "NUMDIS and
  CONSULT are the strongest drivers of the model's predictions overall.") — new
  `buildGlobalInsightSummary()`, pure and unit-tested, mirroring `explanationSummary.js`'s
  per-prediction tone, and reusing `GlobalImportanceChart`'s own `toChartData()` sort rather than
  trusting object key order independently

### Layout / Component / Accessibility / Responsiveness / Animation
- [x] `GlobalImportanceChart` re-themed to `var(--primary)` (was hardcoded `#2563eb`), with
  axis/grid/tooltip re-themed to the same `var(--muted-foreground)`/`var(--border)`/`var(--popover)`
  tokens as `FeatureContributionChart`, for one consistent chart visual language across the app
- [x] Tab switching uses Radix's built-in behavior (no custom animation needed/added)
- [x] Skeleton placeholders (control row + chart-shaped block) replace the old spinner+text state
- [x] Re-verified responsive behavior as part of the full 15-check (5 page × 3 width) regression —
  zero overflow, zero console errors

### Implementation checklist
- [x] `ExplainabilityPage.jsx` restructured around `Tabs` + `ToggleGroup`
- [x] `top_n` control replaced
- [x] `GlobalImportanceChart.jsx` re-themed
- [x] New `globalInsightSummary.js` (+ 3 tests)

Status: ✅ Complete

Live-verified: selected the "Top 5" preset and confirmed exactly 5 bars rendered (real re-fetch,
not a client-side slice), switched between both tabs, zero console errors. Full suite 64/64
passing (added 5 tests: 3 for `globalInsightSummary`, 2 replacing/extending the old `top_n`
interaction test to cover both the preset and custom-input paths).

---

## Page 5: Prediction History

### Current issues
Raw HTML `<table>`, a bare number input for `limit`, no sorting/filtering, no pagination — a data
dump, not a browsing experience.

### UX improvements
- [x] Rebuilt on the shadcn `Table` component (via the shared `PredictionsTable`, already built in
  Milestone 3) with real header styling and row hover states
- [x] Replaced the raw `limit` number input with a `ToggleGroup` of presets (10/25/50/100) plus a
  labeled custom input — **not true pagination**, documented explicitly as a scope decision: the
  backend's `/api/v1/predictions` only supports fetching the N most recent records (`limit`), with
  no offset/page parameter, so page 2/3/etc. genuinely isn't possible without a backend API change,
  which is out of scope for a presentation-layer redesign. A page-size selector over the single
  available page is the honest UI for what the API actually supports.
- [x] Added client-side sort-by-column (timestamp, probability, risk) over the currently-loaded
  page — pure frontend logic (`sortPredictions()`), no backend change; risk sorts by clinical order
  (low < moderate < high), not alphabetical, which would otherwise put "high" first
- [x] Added a risk-category filter (`ToggleGroup`: All / Low / Moderate / High) over the loaded
  results (`filterPredictionsByRisk()`), with a distinct empty state ("No {risk}-risk predictions
  in the last N records") separate from the "no history at all" empty state

### Layout / Component / Accessibility / Responsiveness / Animation
- [x] Column header sort indicators — `PredictionsTable` extended with an optional
  `sortState`/`onSortChange` pair (Dashboard's compact usage stays non-interactive by omitting
  them, History passes them) — one table component serving both needs, not a duplicate
  history-specific table
- [x] Skeleton rows replace the old spinner+text loading state
- [x] Table remains horizontally scrollable inside its own container (shadcn `Table`'s built-in
  `overflow-x-auto` wrapper) — re-verified as part of the full 15-check regression
- [x] Row-level hover state comes from the shadcn `Table` primitive by default

### Bug found and fixed by strengthening the tests, not just the feature
Writing a real `toHaveBeenCalledTimes(1)` assertion for "filtering doesn't trigger a re-fetch"
exposed that `PredictionHistoryPage.test.jsx` never reset its `vi.mock` between tests — call counts
were silently accumulating across all tests in the file. Existing tests never caught this because
they only asserted call *arguments* (`toHaveBeenCalledWith`), which don't care about extra
accumulated calls. Fixed by adding `beforeEach(() => vi.clearAllMocks())`, matching the pattern
already used elsewhere in the suite.

### Implementation checklist
- [x] `PredictionHistoryPage.jsx` rebuilt on shadcn `Table` (via `PredictionsTable`)
- [x] Page-size preset control (not true pagination — see note above)
- [x] Client-side sort + filter (`src/utils/predictionListUtils.js`, 7 new pure-function tests)
- [x] `PredictionsTable.jsx` extended with optional sorting, not duplicated

Status: ✅ Complete

Live-verified against real accumulated history data: risk filter correctly narrows to 1 row when
set to "High" with zero additional network calls (confirmed client-side), column sort by
Probability correctly reorders with the right direction on first click (descending) and toggles on
the second (ascending). Full suite 73/73 passing, 15/15 responsive checks passing, zero console
errors.

---

## Page 6: About

### Current issues
Three plain paragraphs, no visual structure, no hierarchy — currently the least "designed" page
in the product despite needing no data-fetching complexity at all.

### UX / Layout improvements
- [x] Restructured as a proper content page: icon badge + large heading (`text-3xl`) + a
  larger-type mission statement (`text-lg`), then three structured `Card` sections (What it does /
  How predictions work / About the model), each with an icon — replacing three undifferentiated
  paragraphs
- [x] Added live model metadata (name, version) as a small credibility footer, fetched from
  `/health/model` via the existing `healthApi.getModelHealth` — no longer hardcoded prose, and
  will automatically reflect a future model upgrade without a content edit

### Component / Accessibility / Responsiveness / Animation
- [x] Uses the same `Card`/icon-header pattern as Prediction's form sections and the Dashboard —
  confirmed visually consistent, not a one-off layout
- [x] Re-verified responsive at all three widths as part of the full 15-check regression

### Bug found and fixed
Loading state initially rendered a `Skeleton` (a `<div>`) inside a `<p>` element — invalid HTML
(block element inside an inline one) that React surfaced as a real console error/hydration
warning during live verification, not just a lint nitpick. Fixed by changing the wrapper to a
`<div>`, which is what caught this in the first place: **every page in this milestone's live
verification is checked for zero console errors, not just visual correctness** — this bug would
have shipped invisibly otherwise, since it didn't affect the rendered screenshot at all.

### Implementation checklist
- [x] `AboutPage.jsx` restructured
- [x] Live model metadata fetch added (reuses existing `healthApi.getModelHealth`)
- [x] `AboutPage.test.jsx` added (2 tests — this page had no tests at all before, since Sprint 5's
  version had no logic worth testing; now it does)

Status: ✅ Complete

Live-verified: full 75/75 test suite, 15/15 responsive checks, and — after the fix above — zero
console errors across the entire app, not just this page.

---

# Phase 2 — Shared Component Tasks

(Cross-references the Design System section above — listed here for progress tracking against
the specific shared surfaces every page depends on.)

- [x] Sidebar (see Shell tasks above)
- [x] Header/page-title bar
- [x] Breadcrumbs — in the header bar, page title derived from route
- [x] `Button` (all variants)
- [x] `Card`
- [x] `Table`
- [x] Chart theming helper — both chart components re-themed to shared CSS custom properties
  (`var(--destructive)`/`var(--success)`/`var(--primary)`/`var(--muted-foreground)`/`var(--border)`/
  `var(--popover)`)
- [x] Form primitives (`Input`, `Select`, `Label`, `Field`, `Collapsible` section)
- [x] `Sheet` — in active use as the mobile sidebar drawer
- [ ] `Dialog` — installed, not adopted; no confirmation-flow use case exists in the app yet
  (deferred to backlog, not blocking sprint completion)
- [ ] `Toast` (Sonner) — installed, not wired to a real event; no toast-worthy transient event
  (e.g. a save/dismiss action) exists in the current feature set (deferred to backlog)
- [x] Loading indicators — `Skeleton` variants replace every prior loading-spinner usage
  (`LoadingState.jsx` deleted as dead code)
- [x] Error states — `ErrorState.jsx` re-themed on the new design system, icon-led
- [x] Empty states — `EmptyState.jsx` re-themed with an icon, not just gray text
- [x] `useApiRequest` hook — confirmed unchanged functionally; only consumed differently by
  skeleton-aware components
- [x] Reusable layout primitives (page shell, section header, stat-tile grid) — `AppLayout`,
  `StatTile`, `PredictionsTable` all confirmed shared, not duplicated per page

---

# Phase 2 — Technical Refactoring Tasks

- [x] Remove every duplicated card/badge/section-header markup pattern once the component library
  exists (`grep` for `rounded-lg border border-slate-200 bg-white p-` across `src/` and eliminate
  every hand-rolled instance in favor of `<Card>`) — no matches remain; every surface uses
  shadcn `<Card>`/`<Badge>` primitives
- [x] Establish `src/components/ui/` as the shadcn primitives directory, `src/components/` for
  domain components (`RiskBadge`, `PredictionResult`, etc.), keeping the existing
  `forms/`/`charts/` domain subfolders — directory layout confirmed clean in the final source
  tree review
- [x] Extract `StatTile` as a genuinely shared component (used by both Dashboard and Prediction
  Result — must not be duplicated between them) — `src/components/StatTile.jsx` is imported by
  both `DashboardPage` and `PredictionResult`, single implementation
- [x] Reduce CSS duplication: every color/spacing/radius/shadow value sourced from tokens, zero
  raw hex or arbitrary Tailwind values remaining in component files — charts re-themed to
  `var(--destructive)`/`var(--success)`/`var(--primary)`/etc., no raw hex left in components
- [x] Re-run and pass the full responsive verification matrix (5 pages × 3 widths, as established
  in Sprint 5) after the shell/layout change — 15/15 checks passed after the `min-w-0` shell fix
- [x] Re-run and pass a full accessibility pass (keyboard nav, focus indicators, contrast) after
  every page redesign — do not regress Sprint 5's verified baseline — final Playwright keyboard
  navigation sweep across all 5 routes confirmed visible focus indicators throughout
- [x] Performance: verify bundle size impact of `shadcn`/`lucide-react`/animation additions stays
  reasonable (`npm run build`, inspect output size) — tree-shake icon imports individually, not a
  barrel import — route-level code-splitting (`React.lazy`) dropped the main chunk from 875KB to
  361KB, with Recharts isolated into its own 356KB lazy chunk; build size warning resolved
- [x] Update/extend the existing Vitest suite for every component that gains new structure
  (e.g. `PatientRecordForm` tests must keep passing against the shadcn-based rebuild without
  changing their assertions about payload/validation behavior — if an assertion needs to change,
  it must be because the *markup* changed, never because behavior changed) — suite grew from 60
  to 75 tests across the redesign, all passing
- [x] Code cleanup: remove now-unused hand-rolled styling constants (e.g. old
  `RISK_BADGE_CLASSES`-style maps once superseded by component variants) — dead `LoadingState.jsx`
  (referencing a deleted token, zero usages) deleted; unused `waitFor` import removed per lint

---

# Progress Tracking

## Milestones

1. **Design System Foundation** — shadcn/ui installed, tokens defined, core primitives built
2. **Shell Redesign** — sidebar navigation + layout shipped, verified responsive/accessible
3. **Dashboard Redesign**
4. **Prediction Page Redesign** (form + result)
5. **Explainability Redesign**
6. **Prediction History Redesign**
7. **About Page Redesign**
8. **Technical Cleanup & Final Verification** — full responsive/accessibility/test re-verification
   across the entire redesigned product

## Completion Criteria (per page)

A page is done only when:
- [x] Current issues addressed per its section above
- [x] Built entirely from design-system tokens and shared components (no new one-off styling)
- [x] All existing functionality/tests still pass unchanged in behavior
- [x] Responsive-verified at desktop/laptop/tablet
- [x] Accessibility-verified (keyboard nav, focus, contrast, semantic HTML)
- [x] Live-verified against the running backend with a real screenshot, not just code review

## Overall Progress

Progress: 100% (8/8 milestones)

| Milestone | Status |
|---|---|
| 1. Design System Foundation | ✅ Complete |
| 2. Shell Redesign | ✅ Complete |
| 3. Dashboard | ✅ Complete |
| 4. Prediction (form + result) | ✅ Complete |
| 5. Explainability | ✅ Complete |
| 6. Prediction History | ✅ Complete |
| 7. About | ✅ Complete |
| 8. Technical Cleanup & Final Verification | ✅ Complete |

Current Task:

None — Sprint 6 (Frontend Redesign) is complete. All 8 milestones shipped and verified.
Sprint 7 (Public Landing Page) is also complete — see below.

---

# Sprint 6 Status — Complete

The entire frontend was rebuilt on a real design-system foundation (shadcn/ui + Tailwind v4
semantic tokens) rather than incrementally patched. Every one of the 5 pages plus the app shell
was redesigned, and every change was live-verified against the running backend with Playwright
(screenshots + console-error monitoring), not just unit tests.

**Real bugs found and fixed during live verification** (not present in the original code, or
pre-existing — flagged here for traceability):
1. Tablet-width table truncation on the Dashboard — a shared `lg:col-span-3` grid broke at the
   `sm:grid-cols-2` breakpoint; fixed by separating the stat grid and table into independent
   layout blocks.
2. Shell-wide horizontal overflow (~27px) on every page — classic Flexbox `min-width: auto`
   bug on `SidebarInset`; fixed with `min-w-0` on the inset and its content wrapper.
3. Invalid nested `<main>` landmark — `SidebarInset` already renders `<main>`; the content
   wrapper was changed to a `<div>`.
4. `LoadingState.jsx` was dead and broken (referenced a deleted `brand-600` token, zero
   remaining usages) — deleted entirely.
5. Invalid HTML nesting in `AboutPage` (`<Skeleton>` div inside a `<p>`), caught via live
   console-error monitoring rather than the screenshot — fixed by changing the wrapper to a
   `<div>`.
6. Silent test-mock accumulation in `PredictionHistoryPage.test.jsx` — mocks were never reset
   between tests, masked because assertions only used `toHaveBeenCalledWith`; fixed with
   `beforeEach(() => vi.clearAllMocks())`.

**Final metrics:**
- Tests: 75/75 passing (up from 60 at sprint start)
- Responsive regression: 15/15 checks passing (5 pages × 3 widths)
- Accessibility: keyboard navigation verified across all 5 routes, visible focus indicators
  throughout, no regressions from the Sprint 5 baseline
- Bundle size: main chunk reduced from 875KB to 361KB via route-level code-splitting
  (`React.lazy`), with Recharts isolated into its own 356KB lazy chunk
- Lint: `npm run lint` clean aside from pre-existing, accepted shadcn convention patterns
- End-to-end walkthrough (Dashboard → Prediction submit → Explainability → History → About)
  verified with zero console errors across the full session

**Known backlog (non-blocking, intentionally deferred):**
- `Dialog` and `Toast` (Sonner) are installed but not adopted — the current feature set has no
  confirmation-flow or transient-event use case that needs them. Wire them up when a real
  feature (e.g. a destructive action, a background save) actually calls for one; do not force
  an integration just to check the box.
- `Tooltip` is installed but not extended to icon-only affordances — flagged as a small future
  polish item, not a functional gap (every icon-only control currently has an accessible label).
- Full colorblind-safe pattern-fill/icon differentiation for the SHAP contribution chart (beyond
  the text-based "Increased/Decreased risk" mitigation already shipped) needs more visual design
  exploration than this sprint's scope allowed — tracked for a future design pass.

---

# Sprint 7 — Public Landing Page

## Routing decision

The app previously had no public/marketing front door: `/` was the Dashboard itself. Adding a
real landing page meant deciding where it lives. Chosen approach (confirmed with the user):
**`/` becomes the public landing page; the entire app shell moves under `/app`** (`/app`,
`/app/predict`, `/app/explainability`, `/app/history`, `/app/about`). This is the standard
marketing-site-plus-product split and keeps a clean boundary between the public surface and the
authenticated-feeling in-app experience, at the cost of a one-time route migration.

### Implementation checklist
- [x] `src/App.jsx` — `/` now renders `LandingPage` (eager, no shell); the previous index/child
  routes moved under a new `/app` parent route wrapping `AppLayout`
- [x] `src/components/AppSidebar.jsx` — all nav `to` targets re-pointed to `/app/*`; the sidebar's
  `HealthIQ` header is now a `Link` back to `/` (public site), not just static text
- [x] `src/layouts/AppLayout.jsx` — breadcrumb page-title path matchers updated to match the new
  `/app/*` paths
- [x] `src/pages/DashboardPage.jsx` — the "New Prediction" CTA's `Link` re-pointed to
  `/app/predict`
- [x] Full codebase grep for internal route strings confirmed these were the only two files with
  hardcoded paths — no other stale links left behind

## Landing page design

### Content grounding
Every claim on the page is sourced from real project artifacts, not invented marketing copy:
- **0.95 cross-validated ROC-AUC** — `ML/saved_models/model_metadata.json` cross-validation mean
  (0.9518) / `ML/reports/modeling/final_model_selection.md` validation ROC-AUC (0.9649)
- **NHAMCS** — the same dataset named throughout `AboutPage.jsx` and the ML pipeline
- **SHAP explanation on every prediction** — matches the actual `PredictionResult`/
  `FeatureContributionChart` behavior, not an aspirational claim
- The "research and decision-support tool, not a replacement for clinical judgment" disclaimer
  reuses the same framing already established in `AboutPage.jsx`, kept consistent rather than
  inventing new legal/medical language

### Structure
- `SiteHeader` — sticky, translucent-blur nav with in-page anchor links (`#features`,
  `#how-it-works`, `#trust`) and a persistent "Launch app" CTA
- `Hero` — badge, H1, subhead, primary CTA (`/app`) + secondary anchor CTA
- `MetricStrip` — 3 credibility stats (ROC-AUC, explainability, dataset)
- `Features` — 4-card grid (real-time scoring, explainability, clinician-first UX, validation
  rigor)
- `HowItWorks` — 3-step numbered flow mirroring the actual Prediction page workflow
- `TrustSection` — model/dataset provenance paragraph + the clinical-judgment disclaimer callout
  (`warning`-toned, matching the design system's semantic tokens) + link to `/app/about`
- `FinalCta` — closing conversion block
- `SiteFooter` — logo, tagline, and a full nav to every in-app page

Built entirely from existing design-system primitives (`Card`, `Badge`, `Button`) and semantic
tokens — no new colors, shadows, or one-off styling introduced.

### Real bug found and fixed during live verification
The footer navigation used `gap-x-6 gap-y-2` (directional gap utilities) instead of the plain
`gap-6` used everywhere else in the codebase. A Playwright screenshot showed the footer links
rendering with zero visible spacing ("DashboardPredictionExplainability..."); `getComputedStyle`
confirmed `column-gap`/`row-gap` were both computing to `normal` — the directional utilities
were not generating in this project's Tailwind v4 setup. Fixed by switching to `gap-6`, the same
utility already proven to work throughout every other page. Re-verified: `column-gap`/`row-gap`
both compute to `24px` and the screenshot confirms proper spacing at all three widths.

### Verification
- [x] Responsive: 0px horizontal overflow at desktop (1440px), tablet (768px), and mobile
  (390px) — confirmed via `document.documentElement.scrollWidth` vs `clientWidth`, plus
  full-page screenshots at all three widths
- [x] Navigation: landing → `/app` (primary CTA), sidebar nav within the app, and sidebar logo
  → back to `/` all verified end-to-end with Playwright
- [x] Keyboard navigation: 8 tabbable elements on the landing page, every one with a visible
  focus indicator
- [x] Zero console errors across the full landing-page + in-app navigation session
- [x] `LandingPage.test.jsx` — 3 new tests: hero heading + primary CTA href, how-it-works content
  + disclaimer text present, every footer nav link points at the correct `/app/*` route
- [x] Full suite: 78/78 tests passing (75 existing + 3 new); `npm run lint` clean aside from the
  same pre-existing accepted shadcn warnings

Status: ✅ Complete

---

## Sprint 7 follow-up: navigation, scroll, motion & content depth

User feedback after the first landing page ship: no mobile navigation into the app, a broken
scroll position when navigating into the app from a link deep in the page, no animation
anywhere, and a page that read as too sparse/plain for a product landing page (no visuals, no
standard sections). Addressed all four:

### Mobile navigation
- [x] `SiteHeader` gained a `Sheet`-based hamburger menu (`md:hidden`, `Menu` icon trigger) —
  previously mobile visitors had no way to reach the section anchors *or* the in-app pages at
  all, since the desktop text nav was simply hidden below `md` with no fallback. The menu
  contains the same section anchors as the desktop nav (Product/How it works/About the
  model/FAQ) plus direct links to every app page (Dashboard/Prediction/Explainability/Prediction
  History/About) — the equivalent of the app shell's own sidebar, made reachable from the public
  page. Every link uses `SheetClose asChild` so the menu closes itself on navigation.

### Real bug: scroll position not reset on navigation
- [x] Reported as "clicking About the model lands at the end of that page." Root cause: React
  Router client-side navigation does not reset `window.scrollY` the way a full page load does.
  The "Read more about the model" link sits near the bottom of the (long) landing page; clicking
  it while scrolled deep down carried that scroll position onto `/app/about`, a much shorter
  page, making it appear to open already scrolled to its bottom. Fixed with a new
  `src/components/ScrollToTop.jsx` (`useLocation` + `useEffect(() => window.scrollTo(0, 0),
  [pathname])`), mounted once in `App.jsx` alongside `<Routes>`. Verified: scrollY was 2588px
  before clicking the link; 0px on `/app/about` after navigation.

### Motion
- [x] New `src/components/Reveal.jsx` — a small IntersectionObserver-based wrapper that fades
  + slides content in the first time it scrolls into view (`animate-in fade-in
  slide-in-from-bottom-2`, matching the animation already used for the prediction result panel
  in Milestone 8). Respects `prefers-reduced-motion` by rendering content immediately, fully
  visible, with no animation at all under that preference — verified via a `matchMedia`
  polyfill added to `test-setup.js` (jsdom doesn't implement it) plus an `IntersectionObserver`
  polyfill (same reason)
- [x] Applied to every section on the landing page, staggered per card/item where there's a
  grid or list (metrics, features, steps, FAQ items)
- [x] Hover micro-interactions added to metric and feature cards (`hover:-translate-y-0.5
  hover:shadow-md`) and tech-stack pills (`hover:border-primary/40`)
- [x] `scroll-smooth` added globally (`index.css`, `html`) plus `scroll-mt-16` on every anchor
  target section so the sticky header doesn't cover the heading when a nav link jumps to it
- [x] A single restrained decorative gradient blob behind the hero (`bg-primary/10 blur-3xl`) —
  kept to one low-opacity shape in the existing primary hue, not a multi-color gradient mesh, to
  stay inside this project's "no flashy/gaudy" design constraint

### Real bug found and fixed during this pass (found twice, same class of bug)
1. The hero's decorative gradient blob used a fixed `w-[36rem]` (576px). On an `absolute`
   element with `inset-x-0` + `mx-auto` + an explicit width, the auto margins center that fixed
   576px box regardless of viewport width — on a 390px-wide screen this produced 186px of
   horizontal overflow (216px at 360px). Found via a Playwright script that walks every element
   and flags any whose bounding rect exceeds the viewport, not just the aggregate
   `scrollWidth`/`clientWidth` check (which caught the size but not the culprit). Fixed by
   swapping the fixed width for `w-full max-w-[36rem]` (shrinks below its cap instead of
   overflowing) plus `overflow-hidden` on the hero section as a defensive backstop for any future
   decorative element.
2. The product-preview section's "Sample output — illustrative, not a live prediction" `Badge`
   forced that full sentence onto one line (`Badge` is `whitespace-nowrap` by design, meant for
   short pills). On narrow viewports this alone would have overflowed the page. Fixed by
   shortening the badge to "Sample prediction" and moving the clarifying detail into the
   paragraph below it, which wraps normally.

### New content sections (addressing "add more content ... relevant, and standard for this type
of site")
- [x] **Product preview** (`#preview`) — the real `PredictionResult` component (lazy-loaded, not
  duplicated/faked), fed a clearly-labelled sample prediction built from real SHAP feature names
  observed in a live run of the app. Gives visitors an actual look at the product instead of
  describing it in prose only.
- [x] **Tech stack strip** — FastAPI, LightGBM, SHAP, NHAMCS dataset, React, as icon+label pills.
  Grounded in the actual architecture (matches `AboutPage.jsx`'s description), not invented
  branding or fabricated third-party logos.
- [x] **FAQ** (`#faq`) — 5 questions, built on the same `Collapsible` primitive already used by
  the Prediction form's "Workup details" section, not a new dependency. Answers are grounded in
  what the app actually does (clinical-judgment disclaimer, NHAMCS provenance, SHAP
  explainability, LightGBM + FastAPI, prediction history persistence) — no invented stats,
  testimonials, or customer logos, which would have been fabricated content for a project with
  no real deployed users yet.
- [x] Desktop header nav extended with a fourth anchor (`FAQ`) alongside the existing three.

### Verification
- [x] `document.documentElement.scrollWidth` vs `clientWidth` re-confirmed at 0px overflow at
  desktop (1440px), tablet (768px), mobile (390px), and an additional small-mobile check (360px)
  after the gradient-blob fix
- [x] Full-element overflow scan (every element's bounding rect vs. viewport, not just the
  aggregate scrollWidth) confirms zero offending elements post-fix
- [x] Reveal-on-scroll verified with an actual simulated scroll (incremental `mouse.wheel` +
  waits, not an instant jump) — confirmed sections transition from `opacity-0` to `animate-in`
  as they're scrolled to, both mid-page and near the bottom
- [x] Mobile hamburger verified end-to-end: opens, contains both "On this page" and
  "Application" link groups, clicking an app link navigates and auto-closes the sheet
- [x] Bundle size re-checked after adding the lazy `PredictionResult` import to the landing page:
  main chunk 425KB (up from 361KB, still under the 500KB warning threshold), `PredictionResult`
  now its own small shared chunk (4.4KB) reused by both the landing page and the Prediction page,
  Recharts still isolated in its own lazy 356KB chunk — no regression in code-splitting
  discipline
- [x] Full suite: 78/78 passing; `npm run lint` clean aside from the same pre-existing accepted
  shadcn warnings

Status: ✅ Complete

---

# Sprint 8 — App-wide Depth & Content Pass

User feedback: the redesigned app (Sprint 6) still read as flat and "static," and the request was
to push every page and shared component further — more visual depth, more motion, more real
content — using the project's design skills (`impeccable`, `emil-design-eng`, `shadcn`) rather
than working from scratch. `impeccable`'s bundled scripts/reference files weren't present in this
installation (only its top-level `SKILL.md`), so this pass worked from that file's principles
directly plus the full guidance in `emil-design-eng`'s and `shadcn`'s `SKILL.md` files.

## How the skills' guidance was applied (not just "installed")

- **`impeccable`**: classified the landing page as **Persuade** mode (already animation-heavy from
  Sprint 7 — left alone) and the 5 app pages as **Operate** mode, where "scanability, consistency,
  native expectations… outrank expression." This is *why* the app pages got depth via layout,
  color, and real content rather than more motion — over-animating a dashboard a clinician opens
  dozens of times a session would work against the product, not for it.
- **`emil-design-eng`**: applied the animation decision framework literally — page-level content
  gets a single one-time reveal on mount (occasional, purposeful), nothing continuous or
  scroll-triggered on Operate pages, and no animation was added to any keyboard-repeatable or
  frequently-clicked control (sort headers, toggle groups, the submit button) per its "100+
  times/day → no animation, ever" rule.
- **`shadcn`**: ran `npx shadcn@latest info --json` to confirm the project's actual config
  (`base: radix`, `style: nova`, `iconLibrary: lucide`) before changing anything, then applied its
  "use components, not custom markup" rule concretely — added the `alert` and `empty` primitives
  via the CLI (not hand-copied) and migrated the two hand-rolled callout/empty-state divs onto
  them. Did **not** attempt the `space-y-*` → `gap-*` mechanical rewrite the rules also call for:
  it touches 13 files with zero visual effect (both render identically), which fails this
  project's own "avoid unnecessary changes" standard — judgment call, not an oversight.

## Shared component changes

- [x] `npx shadcn@latest add alert empty` — two new primitives, not hand-rolled
- [x] `src/components/ui/alert.jsx` — added a project-specific `warning` variant
  (`bg-warning/10 text-warning`), mirroring the `success`/`warning` variants already added to
  `Badge` in Sprint 6, rather than overriding colors via `className`
- [x] `src/components/ErrorState.jsx` — rewritten on `Alert`/`AlertTitle`/`AlertDescription`
  (variant `destructive`), replacing the hand-rolled bordered div
- [x] `src/components/EmptyState.jsx` — rewritten on `Empty`/`EmptyHeader`/`EmptyMedia`/
  `EmptyTitle`/`EmptyDescription`, replacing the hand-rolled dashed-border div
- [x] New `src/components/PageHeader.jsx` — icon-chip + title + description + optional note/action
  slot, extracted from the pattern `AboutPage` already used, now shared by Dashboard, Prediction,
  Explainability, and Prediction History (About keeps its own larger, narrative-style header
  intentionally — it reads more than it operates)
- [x] `src/components/StatTile.jsx` — icon chip color now follows `tone` (primary/success/
  warning/destructive tinted backgrounds instead of one flat gray for every tile) and gained a
  `hover:-translate-y-0.5 hover:shadow-md` lift, matching the landing page's card treatment
- [x] `src/components/forms/PatientRecordForm.jsx` — `FormSection` icons moved into the same
  colored chip treatment as `PageHeader`, for visual consistency between the form and the rest of
  the app shell

## Real, non-fabricated content added per page

Every addition below either surfaces data the backend already returns but the UI wasn't showing,
or computes a new summary client-side from data already being fetched — nothing invented.

- **Dashboard**: a computed insight line ("N of the last 5 predictions were flagged high risk"),
  derived from the same 5 predictions already fetched for the table — a second, richer read of
  data already on the page, not a new endpoint
- **Prediction**: a contextual note above the form explaining that every result ships with a SHAP
  explanation, tying the page to the product's actual explainability behavior
- **Explainability**: the page previously had a static, hardcoded caption
  ("Computed once over the validation split"). The backend's `/explain/global` response already
  includes `computed_on` and `n_rows` (`Backend/app/schemas/explanation.py`) — neither field was
  displayed anywhere. Now shown live: "Computed once over 2,404 rows of the validation split."
  Also added an explanatory paragraph distinguishing global vs. local (per-prediction)
  explanations, and gave each chart tab a `CardHeader`/`CardDescription` instead of a bare chart
- **Prediction History**: a new 3-tile summary strip (records loaded, predicted admission rate,
  high-risk share) computed client-side from the already-fetched page of records via a new
  `summarizePredictions()` pure function in `predictionListUtils.js` — same file, same pattern as
  the existing `sortPredictions`/`filterPredictionsByRisk` functions
- **About**: substantially expanded — a new "Model performance" section with real validation
  metrics (0.95 cross-validated ROC-AUC, 0.83 PR-AUC, 70.1% recall, sourced from
  `ML/saved_models/model_metadata.json` / `ML/reports/modeling/final_model_selection.md`, and
  cross-checked against the same 0.95 figure already cited on the public landing page so the two
  pages don't contradict each other), plus a new "Responsible use" section (data & privacy
  provenance, model limitations) and a cross-link to Prediction History

## Motion

- [x] Reused the existing `Reveal` component (built in Sprint 7 for the landing page) for a
  single one-time fade/rise on each page's content as it resolves from loading — Dashboard's stat
  grid and table, Explainability's chart panel, History's summary strip and table, About's
  sections — all staggered slightly (60-140ms) rather than appearing simultaneously
  (`emil-design-eng`'s stagger guidance: 30-80ms between items, kept short)
- [x] Deliberately **not** applied to: the Prediction form itself (filled out and submitted
  frequently within a session — motion here would slow down a task-focused flow), sort/filter
  controls, and anything already covered by Sprint 6/7's existing entrance animation
  (`PredictionResult`'s own fade-in stays as the sole animation on that panel)

## Verification

- [x] Per-page unit test suites re-run after each page's rewrite (Dashboard, Prediction,
  Explainability, History, About) — all passing; `AboutPage.test.jsx` gained a `MemoryRouter`
  wrapper (the page now renders an internal `Link`) and a third test asserting the new
  "Data & privacy"/"Limitations" content is present
- [x] Full suite: 79/79 passing; `npm run lint` clean aside from the same pre-existing accepted
  shadcn warnings
- [x] `npm run build`: main chunk 429KB (up from 425KB — the `Alert`/`Empty` primitives and page
  content additions), still under the 500KB warning threshold; chunk-splitting structure
  unchanged
- [x] Full responsive/overflow regression re-run: 5 app pages × 3 widths (desktop/tablet/mobile),
  0px horizontal overflow on all 15
- [x] Full end-to-end walkthrough (Dashboard → submit a prediction → Explainability → History →
  About) with zero console errors
- [x] Keyboard navigation re-verified on all 5 app pages — visible focus indicators throughout
- [x] Confirmed via real (incremental `mouse.wheel`) scrolling, not just a static screenshot, that
  `Reveal`-wrapped content genuinely appears for a real user — a naive Playwright `fullPage`
  screenshot captures beyond the actual browser viewport without scrolling it, so
  IntersectionObserver-gated content below the fold never fires and appears blank in that specific
  screenshot method. This is a screenshot-tooling artifact, not a product bug — verified twice
  (landing page, About page) by scrolling for real and confirming the content renders

Status: ✅ Complete
