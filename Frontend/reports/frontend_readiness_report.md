# Milestone 1 — Environment Verification & Scaffolding Report

Sprint 5 (Frontend Integration) — Milestone 1

---

## 1. Backend verification

Started the backend locally (`uvicorn Backend.app.main:app`) and confirmed every endpoint this
sprint depends on responds as documented:

| Endpoint | Result |
|---|---|
| `GET /health` | 200 |
| `GET /health/model` | 200, `lightgbm` v1.0.0 |
| `GET /health/db` | 200 |
| `GET /api/v1/explain/global?top_n=3` | 200, well-formed |
| `GET /api/v1/predictions?limit=1` | 200, well-formed |

**Backend addition required for this sprint**: the backend had no CORS configuration, so a
browser-based Vite dev server would have been blocked from calling it entirely. Added
`CORSMiddleware` (`Backend/app/main.py`) plus a `cors_allowed_origins` setting
(`Backend/app/core/config.py`, defaulting to the Vite dev server's origins,
`http://localhost:5173`/`http://127.0.0.1:5173`), covered by 3 new tests
(`Backend/tests/test_cors.py`). Full backend suite: **73/73 passing**.

## 2. Scaffolding

Created `Frontend/` via `npm create vite@latest -- --template react` (JavaScript, per
`PROJECT_CONTEXT.md` §18's "ES6+", not TypeScript) and added:

- `tailwindcss` + `@tailwindcss/vite` (Tailwind v4's Vite-plugin integration — no separate
  `tailwind.config.js`/PostCSS setup needed; theme customization lives in `src/index.css` via
  `@theme`)
- `react-router-dom`
- `axios`
- `recharts`

Removed the Vite template's default splash content (`App.css`, template `App.jsx`, unused
`react.svg`/`vite.svg`/`hero.png`/`icons.svg` assets) since this is a real application, not a
starter demo.

### Folder structure

```
Frontend/src/
├── pages/        (built out from Milestone 4 onward)
├── components/
├── services/     (Milestone 2)
├── hooks/        (Milestone 2)
├── layouts/      (Milestone 3)
├── App.jsx
├── main.jsx
└── index.css     (Tailwind entry + theme tokens)
```

### Configuration

`VITE_API_BASE_URL` (`.env`/`.env.example`) holds the backend base URL — never hardcoded in
components. Defaults to `http://localhost:8000`, matching the backend's default `uvicorn` port
and the CORS origin configured above.

## 3. Dependency note (transparent, not hidden)

`npm audit` flags `react-router-dom`/`react-router` with several high-severity advisories
spanning nearly the entire 6.x-8.x range. Inspected the advisory list: the majority are
SSR/RSC-specific (React Server Components mode, server actions, `__manifest` endpoint,
`ScrollRestoration` SSR) which do not apply to this app — a pure client-rendered SPA via
`vite build`, no SSR, no RSC, no server loaders/actions. Checked whether an older pin avoided
them: it does not — 7.11.0 falls under a *different*, broader advisory bundle. Kept the latest
version (`7.18.2`) as the most actively maintained option rather than downgrading into an
equally-flagged range. The client-relevant items (open-redirect via `<Link>`/`useNavigate`) are
mitigated by this app never routing based on unvalidated external input. Worth re-checking before
a real production deployment, not a blocker for this sprint.

## 4. Verification

- `npm run dev` starts cleanly (Vite v8.2.0, ready in <1s)
- `GET http://localhost:5173/` → 200, correct `<title>HealthIQ</title>`
- Confirmed `import.meta.env.VITE_API_BASE_URL` resolves to `http://localhost:8000` in the served
  module (checked via the dev server's transformed module output)
- Tailwind utility classes present in `App.jsx` (`min-h-screen`, `flex`, etc.) via the `@theme`-based
  v4 setup

Status: Milestone 1 complete. Ready for Milestone 2 (API client layer).

---

## Milestone 2 — API Client Layer

Built `src/services/apiClient.js` (a single Axios instance) plus one module per backend resource
(`predictionApi.js`, `explainApi.js`, `historyApi.js`, `healthApi.js`), and `src/hooks/useApiRequest.js`
(one `{ data, loading, error, execute }` pattern reused by every page, supporting both
auto-fire-on-mount reads and manually-triggered actions like a form submit).

The Axios response interceptor unwraps the backend's `SuccessResponse` envelope once
(`unwrapSuccessResponse`) and normalizes every failure mode -- backend `ErrorResponse`, or a raw
network failure with no response at all -- into a single `ApiError` class (`normalizeError`), so
no component ever branches on where an error came from.

### Tests

16/16 passing (`npm test`, Vitest + jsdom + React Testing Library):
- `apiClient.test.js` — envelope unwrapping, backend error normalization (with field errors),
  network-failure normalization, generic-message fallback
- `predictionApi.test.js`, `explainApi.test.js`, `historyApi.test.js`, `healthApi.test.js` — each
  resource module calls the right method/path/params (mocked `apiClient`)
- `useApiRequest.test.js` — immediate vs. manual firing, resolved data, captured (not thrown)
  rejection, manual `execute()`

### Live end-to-end verification (not just mocked tests)

Backend addition required to unblock this at all: added CORS support (see Milestone 1). Then,
with both the real backend (`uvicorn`, port 8000) and the real Vite dev server (port 5173)
running, wired `App.jsx` to call `getModelHealth()` through `useApiRequest` and drove a real
headless Chromium browser against it (Playwright, since `chromium-cli` was not available in this
environment) rather than relying on `curl` (which cannot execute the page's JavaScript or verify
CORS actually works from a browser context):

- Page rendered "Model loaded: lightgbm v1.0.0" — a value that only appears if the browser's
  `fetch` actually reached the FastAPI backend, passed the CORS preflight, and the response
  envelope was unwrapped correctly
- Zero browser console errors
- Screenshot confirmed correct rendering and Tailwind styling

This is the real proof this milestone needed: not "the code looks right" but "a browser served by
Vite successfully called the FastAPI backend and displayed live data."

Status: Milestone 2 complete. Ready for Milestone 3 (Navigation & Layout).

---

## Milestone 3 — Navigation & Layout

### Scope correction

`PROJECT_CONTEXT.md` §79 lists Model Comparison and Dataset Analytics as possible nav sections.
The Sprint 4 backend implements neither (one production model only, no dataset-analytics
endpoint). Per CLAUDE.md's "avoid placeholder implementations," navigation was scoped to what the
backend actually supports -- Dashboard, Prediction, Explainability, Prediction History, About --
rather than shipping dead links or fabricated static pages. Documented in `TASKS.md` as
backend-dependent future work.

### Built

- `src/components/LoadingState.jsx`, `ErrorState.jsx` (renders field-level validation errors from
  the backend's `ErrorResponse.errors`, plus an optional retry button), `EmptyState.jsx`
- `src/components/Navigation.jsx` -- active-route highlighting via `NavLink`
- `src/layouts/AppLayout.jsx` -- shared shell (`Navigation` + `<Outlet />`)
- `src/App.jsx` / `src/main.jsx` -- `react-router-dom` route tree wrapped in `BrowserRouter`
- Stub pages for Prediction, Explainability, and Prediction History (fleshed out in Milestones
  5/7/8); `DashboardPage.jsx` seeded with the real model-health card from Milestone 2's `App.jsx`
  rather than discarding it; `AboutPage.jsx` written in full now since it has no API dependency

### Live verification

With both real servers running, drove headless Chromium through every route:

- `/`, `/predict`, `/explainability`, `/history`, `/about` each render the expected `<h1>` — 5/5
- Clicking the "Prediction" nav link from the Dashboard navigates to `/predict` (real `NavLink`
  click, not a direct URL load)
- Checked layout at both a 1280px desktop width and an 820px tablet width (screenshots) — nav and
  content reflow without breaking, no horizontal scroll, per PROJECT_CONTEXT.md §93
- Zero console errors across all of the above

Status: Milestone 3 complete. Ready for Milestone 4 (Dashboard Page).

---

## Milestone 4 — Dashboard Page

Built out `DashboardPage.jsx` in full:

- **System health card**: three independently-fetched rows (API liveness, model, database), each
  with its own loading/error/retry state — a failing row never blanks the others or the rest of
  the page (this was explicitly required and is unit-tested, not just visually eyeballed)
- **Recent predictions card**: last 5 predictions via `listPredictions(5)`, with a genuine empty
  state when there's no history yet
- **Quick-navigation cards**: New Prediction, Explainability, Prediction History (Dataset
  Analytics omitted — no backend endpoint, per the Milestone 3 scope correction)

### Tests

19/19 passing. Added `DashboardPage.test.jsx` (3 tests): one card failing (mocked
`getModelHealth` rejection) leaves the rest of the dashboard intact, the empty-history state
renders correctly, and populated history renders correctly. Needed
`@testing-library/jest-dom` + a Vitest `setupFiles` entry (`src/test-setup.js`) to get
`toBeInTheDocument()` working — not present after the Milestone 2 test setup.

### Live verification

With both real servers running (and real prediction history already in the database from earlier
milestones' live checks), loaded the Dashboard in headless Chromium: all three health rows show
correct live data (`lightgbm v1.0.0`, both liveness/DB "OK"), five real historical predictions
render with correct timestamps/risk categories/probabilities, all three quick-nav cards render.
Zero console errors. Screenshot confirms a clean, professional layout.

Status: Milestone 4 complete. Ready for Milestone 5 (Patient Prediction Interface).

---

## Milestone 5 — Patient Prediction Interface

### Coded-field labels resolved before building the form

The open question from Sprint 4 (raw NHAMCS codes for `sex`/`race_ethnicity`/`triage_level`, no
confirmed value-label table) was resolved by extracting
`Data/documents/technical Documentation.pdf` with `pdftotext -layout` and grepping the actual
codebook entries -- not guessed:

- `SEX`: 1 = Female, 2 = Male
- `RACERETH`: 1 = Non-Hispanic White, 2 = Non-Hispanic Black, 3 = Hispanic, 4 = Non-Hispanic Other
- `IMMEDR` (triage): 1 = Immediate, 2 = Emergent, 3 = Urgent, 4 = Semi-urgent, 5 = Non-urgent

This also independently confirmed the two boolean mappings the backend already assumed
(`ARREMS` 1=Yes/2=No, `CONSULT` 0=No/1=Yes) were correct. `Backend/app/schemas/patient.py`'s
`Field` descriptions were updated with the confirmed labels (wire format unchanged -- only
documentation and the frontend's option text needed them).

### Built

- `src/components/forms/patientFieldOptions.js` -- the confirmed label tables
- `src/components/forms/patientRecordFormConfig.js` -- pure functions: `validatePatientRecordForm`
  (mirrors the backend's exact constraints so invalid submissions never reach the network) and
  `buildPatientRecordPayload` (converts string form state to correctly-typed values, omitting
  every field the user left blank so the backend's imputation handles it)
- `src/components/forms/FormField.jsx` -- reusable `TextField`/`SelectField` with inline errors,
  `aria-invalid`/`aria-describedby`/`aria-required`
- `src/components/forms/PatientRecordForm.jsx` -- the full form, grouped into Demographics /
  Vitals / Triage & Arrival / Workup, matching `PatientRecordRequest` field-for-field
- `PredictionPage.jsx` wired to call `submitPrediction` via `useApiRequest`, with a minimal (real,
  not placeholder) result summary -- the full chart-based explanation view is Milestone 6

### Bug found and fixed by the tests (not just detected, root-caused)

`useApiRequest`'s `execute` originally re-threw on failure ("so callers can await it if needed" --
speculative, unused). Every actual call site in this app passes `execute` directly as an event
handler (`onSubmit`, `onClick`) without awaiting it, so a rejection became an **unhandled promise
rejection** with no user-visible effect -- caught by `PredictionPage.test.jsx`'s failure-path test,
not by manual testing. Fixed at the source: `execute` no longer re-throws (state already captures
the error); this removes the footgun from every current and future call site, including the
Dashboard's retry buttons which had the identical latent bug.

### Tests

40/40 passing. Added: `patientRecordFormConfig.test.js` (11 tests -- validation and payload-building
pure functions), `PatientRecordForm.test.jsx` (4 tests -- renders human-readable labels not raw
codes, blocks submission with errors when incomplete, submits a correctly-typed payload, disables
the button while submitting), `PredictionPage.test.jsx` (2 tests -- success and failure paths).
Also fixed a cross-test pollution bug: React Testing Library's automatic cleanup never fired
because `vite.config.js` has `globals: false`; added explicit `afterEach(cleanup)` to
`test-setup.js`.

### Live verification

With the real backend running, drove the form through headless Chromium:
1. Submitted empty -- 9 field-level validation errors shown, zero network calls made (confirmed no
   request reached the backend)
2. Filled a genuinely distinct patient record (72-year-old female, tachycardic, hypoxic, arrived by
   ambulance, Emergent triage) using the human-readable dropdowns and submitted for real
3. Backend returned a real prediction (17.4% admission probability, Low Risk, No admission
   predicted) -- rendered correctly, zero console errors

Status: Milestone 5 complete. Ready for Milestone 6 (Prediction Result & Explainability Interface).

---

## Milestone 6 — Prediction Result & Explainability Interface

### Built

- `src/components/RiskBadge.jsx` -- extracted from `PredictionPage` so it can be reused by
  Milestone 8's history table without duplicating the color-mapping logic
- `src/components/charts/explanationSummary.js` -- pure `buildExplanationSummary()`, turns the top
  increased/decreased-risk features into one plain-language sentence (PROJECT_CONTEXT.md §83:
  understandable without ML expertise)
- `src/components/charts/FeatureContributionChart.jsx` -- a single diverging Recharts bar chart
  (red = increased risk, green = decreased risk) combining both directions ranked by SHAP
  magnitude, rather than two separate top-N lists; exports `selectTopContributions()` as a pure,
  independently-tested function
- `src/components/PredictionResult.jsx` -- the full result view: risk badge, predicted outcome,
  admission probability / confidence / baseline rate / model version stat grid, the plain-language
  summary, and the chart with a color legend
- `src/utils/formatPercentage.js` -- found during live verification (see below) and fixed

### Bug found during live verification, not just cosmetic

The live check showed "Baseline rate: 0.0%" for a real backend response where the actual value was
0.025% -- technically correct after rounding, but reads as broken/zero to a user. Added
`formatPercentage()`: values under 0.1% get 3 decimal places instead of 1, so a genuinely small
but non-zero rate reads as "0.025%," not "0.0%". Applied to all three probability stats in
`PredictionResult`.

### Tests

51/51 passing. Added: `explanationSummary.test.js` (3 tests), `FeatureContributionChart.test.js`
(5 tests -- ranks by magnitude regardless of direction, sorts for a clean diverging chart, caps at
maxFeatures, does not mutate inputs, handles empty input), `formatPercentage.test.js` (3 tests),
and updated `PredictionPage.test.jsx`'s success-path assertions for the fuller result view (model
version, plain-language summary text).

### Live verification

Submitted a second, distinct realistic patient record (81-year-old male, tachycardic, hypotensive,
hypoxic at 89%, ambulance arrival, Immediate triage, 4 discharge diagnoses) against the real
backend. Result rendered correctly: 35.2% admission probability, Low Risk, a diverging 8-feature
chart (`CONSULT__Yes` as the largest red bar, `NUMDIS` as the largest green bar), the correct
plain-language summary sentence, and -- after the fix above -- an accurate "0.025%" baseline rate
instead of a misleading "0.0%". Zero console errors, both before and after the fix.

Status: Milestone 6 complete. Ready for Milestone 7 (Global Explainability / Model Insights Page).

---

## Milestone 7 — Global Explainability / Model Insights Page

### Built

- `src/components/charts/GlobalImportanceChart.jsx` -- single-color horizontal bar chart, plus a
  pure exported `toChartData()` that defensively re-sorts the backend's `{feature: value}` object
  (object key order isn't a contract worth relying on even though the backend already sorts it)
- `ExplainabilityPage.jsx` -- adjustable `top_n` control (clamped client-side to the backend's
  1-866 range) driving `useApiRequest`'s `params` re-fetch, with two side-by-side charts ("By
  encoded feature" and "By source variable") matching the two keys `get_global_explanation`
  returns

### Tests

56/56 passing. Added `GlobalImportanceChart.test.js` (2 tests) and `ExplainabilityPage.test.jsx`
(3 tests: loads with the default `top_n=20` on mount, re-fetches when `top_n` changes, shows an
error state on failure).

### Live verification

Loaded the page against the real backend: both charts render real validation-split importance
data (`NUMDIS`, `CONSULT__Yes`/`CONSULT`, `TOTDIAG` at the top of both, as expected from Sprint 3's
findings). Changed `top_n` from 20 to 5 and confirmed both charts re-fetched and re-rendered with
exactly 5 bars each. Zero console errors.

Status: Milestone 7 complete. Ready for Milestone 8 (Prediction History Page).

---

## Milestone 8 — Prediction History Page

### Built

`PredictionHistoryPage.jsx`: a table (timestamp, outcome, probability, risk badge, model
name/version, processing time) fed by `listPredictions()`, an adjustable `limit` control (clamped
to the backend's 1-500 range), reusing `RiskBadge`, `EmptyState`, `LoadingState`, `ErrorState`, and
`formatPercentage` from earlier milestones rather than duplicating any of them.

### Tests

60/60 passing. Added `PredictionHistoryPage.test.jsx` (4 tests: loads with the default limit,
empty state, re-fetch on limit change, error state).

### Live verification

Loaded against the real backend (with real history accumulated from every earlier milestone's
live checks): three real historical predictions render correctly with accurate timestamps,
probabilities, risk badges, and processing times. Changing the limit to 3 correctly re-fetched and
rendered exactly 3 rows. Zero console errors.

Status: Milestone 8 complete. Ready for Milestone 9 (Polish, Accessibility & Responsive Verification).

---

## Milestone 9 — Polish, Accessibility & Responsive Verification

### Responsive verification (systematic, not spot-checked)

Every route (`/`, `/predict`, `/explainability`, `/history`, `/about`) checked at three widths —
desktop (1440px), laptop (1024px), tablet (768px) — 15 checks total, measuring
`document.documentElement.scrollWidth` vs `clientWidth` to detect horizontal overflow
programmatically rather than eyeballing screenshots. **Zero overflow anywhere.** Visually
confirmed the two highest-risk layouts at tablet width: Explainability's two-column chart grid
correctly stacks to one column, and the History table remains fully legible without a horizontal
scrollbar (a bit tight in the nav bar at 768px, but usable — acceptable given
PROJECT_CONTEXT.md §93 treats tablet as secondary to desktop/laptop).

### Accessibility pass

- **Keyboard navigation**: tabbed through the Dashboard from page load — focus moves through the 5
  nav links then the 3 quick-nav cards in a sensible order, every focused element has a visible
  native focus outline (verified programmatically via computed `outline-style`, not assumed), and
  pressing Enter on a keyboard-focused nav link actually navigates (real keyboard activation, not
  a click simulation).
- **Semantic HTML**: headings (`h1`/`h2`/`h3`) used consistently for page/section structure; forms
  use native `<label>` wrapping (a valid, accessible association method) plus
  `aria-invalid`/`aria-describedby`/`aria-required` on every form field; the History table uses a
  real `<table>` with `<th scope="col">`; validation errors use `role="alert"`.
- **Color contrast**: dark slate text on white/light backgrounds throughout; risk badges and error
  states use sufficiently dark text-on-light-background pairs (e.g. `text-red-700` on `bg-red-50`,
  not `text-red-400`).

### About page

Already written in full during Milestone 3 (no API dependency, so there was no reason to defer
it) — no changes needed here.

### Consolidated end-to-end walkthrough

Beyond every individual milestone's own live verification, ran one continuous browser session
covering the full user journey in order: Dashboard loads live model status → navigate to
Prediction via a real nav click → submit a fresh, distinct patient record (55yo male, Hispanic,
normal vitals, Semi-urgent triage, not by ambulance) → view the result with its chart → navigate to
Explainability and confirm global insights load → navigate to Prediction History and confirm the
just-submitted prediction appears as the most recent row. **Zero console errors across the entire
session**, not just per-page.

Status: Milestone 9 complete. Ready for Milestone 10 (Ready for Review).
