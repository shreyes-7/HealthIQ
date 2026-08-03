# Backend Readiness Report

Sprint 4 (Backend Integration) — Milestone 9

---

## 1. What was built

A versioned FastAPI backend (`Backend/app/`) exposing the Sprint 2 production model
(`ML/saved_models/model.pkl`) and the Sprint 3 explainability layer
(`ML/explainability/service.py`) as a REST API, with request validation, prediction history
persistence, health monitoring, structured logging, and automated tests. The backend never
trains, retrains, or refits anything — every ML artifact is loaded once, at startup, via
`Backend.app.services.explanation_service.ExplanationRuntime`.

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Service identity/status |
| GET | `/health` | Liveness |
| GET | `/health/model` | Confirms model + SHAP explainer are loaded |
| GET | `/health/db` | Confirms database connectivity |
| POST | `/api/v1/predict` | Curated patient record → prediction + explanation (always both, per CLAUDE.md) |
| GET | `/api/v1/explain/global` | Precomputed Sprint 3 global feature importance |
| GET | `/api/v1/predictions` | Prediction history, most recent first |

### Design decision carried through the whole sprint

`PreprocessingPipeline.transform()` requires all ~900 raw NHAMCS columns to be *present*
(several cleaning steps index a fixed, previously-learned column list without an existence
check — a missing column raises `KeyError`, not just a null). Requiring a client to submit ~900
fields would violate the "simple form, minimal effort" product requirement. Confirmed with the
user (Milestone 4): the request schema exposes an ~18-field curated clinical subset, and
`Backend.app.services.patient_record_assembler.PatientRecordAssembler` fills every other raw
column with null before calling `transform()`, relying entirely on the pipeline's own
already-fitted median / "Missing"-category imputation — no new imputation logic was introduced.
Verified empirically at Milestone 4 and re-verified end-to-end at Milestone 9 (Section 3 below).

## 2. Test suite

**70/70 tests passing** (`Backend/tests/`, run via `python -m pytest Backend/tests/`), covering:

- Configuration defaults and environment overrides
- The ML service layer (`ExplanationRuntime`, model-compatibility check, `predict_and_explain`)
- Request schema validation (missing/invalid/unexpected fields)
- The patient-record assembler (raw column coverage, unit conversions, zero-NaN pipeline output)
- API-level tests for `/predict`, `/explain/global`, `/predictions` (`TestClient`)
- Database persistence (isolated in-memory DB for unit tests, plus an API-level round trip)
- Health endpoints, including simulated model/database unavailability
- Error handling: validation errors, simulated prediction failures, simulated database failures,
  unknown routes — every case verified to return the common `ErrorResponse` envelope without a
  stack trace or internal path in the message
- Logging: verified the prediction log line never contains submitted patient field values

## 3. Live end-to-end verification (not just the test suite)

Per this milestone's requirement, a genuinely fresh raw patient record — row 15428 of the raw
NHAMCS dataset, never touched by any earlier milestone, test, or example in this sprint — was
selected programmatically (filtered to rows with non-sentinel values for every curated field) and
POSTed to a **running `uvicorn` server** (not `TestClient`):

- `GET /health`, `/health/model`, `/health/db` → all 200
- `POST /api/v1/predict` → 200, well-formed prediction + explanation
- `GET /api/v1/predictions?limit=1` → 200, confirmed the prediction above was persisted

## 4. Performance finding

Sprint 3 (Milestone 8) reported ~1.2s per fresh-record explanation. Measuring the same
`ExplanationRuntime.explain_raw_patient()` call in this sprint consistently shows **~2.3-2.6s**,
including:

- A fully-populated real raw row (all 913 columns present, no assembler involved): ~2.3-2.6s
- The assembler's mostly-null curated record (99% of columns null): ~2.5-2.6s

These two are statistically indistinguishable — **the curated-subset/auto-fill design is not the
cause of the increase**; a fully-populated row is exactly as slow. The regression reproduces in a
single call in a completely fresh Python process, ruling out test-session warm-up effects. The
root cause was not conclusively identified in this sprint (candidates: general machine load while
this sprint's work was in progress, or a dependency-version difference introduced when
`fastapi`/`sqlalchemy`/etc. were installed alongside the existing ML dependencies). **Flagged as
a follow-up investigation, not fixed here** — root-causing SHAP/LightGBM performance is a
Machine Learning subsystem concern (`ML/explainability/`), not a backend one, and this sprint did
not modify any ML code.

**Practical implication**: at ~2.5s per request, `/api/v1/predict` is workable for a demo or a
clinician submitting one patient at a time, but is borderline for interactive use at higher
request volume. If sub-500ms latency becomes a requirement, recommended next steps (for a future
sprint, in `ML/`) are profiling `PreprocessingPipeline.transform()` and `TreeExplainer` calls in
isolation to localize the cost, and considering response-time optimizations such as background
persistence (the `history_service.record_prediction()` call currently happens synchronously
within the request).

## 5. Known limitations / documented scope decisions

- Coded fields (`sex`, `race_ethnicity`, `triage_level`) are passed through as raw NHAMCS codebook
  values rather than translated to human-readable labels (Milestone 4) — the codebook layout file
  available in this repository documents field names, not value-label tables, and guessing the
  Yes/No or category orientation wrong was judged riskier than shipping raw codes with descriptive
  `Field` docs. Frontend-sprint follow-up once the value-label tables are confirmed.
- Prediction history intentionally does not store the patient's submitted input (age/vitals/etc.),
  only the prediction outcome and a small "explanation reference" — matches
  `PROJECT_CONTEXT.md` §64's field list and CLAUDE.md's "never log/store sensitive information."
- No authentication/authorization — explicitly out of scope for this sprint per
  `PROJECT_CONTEXT.md` §65/§66 ("optional for the initial version"); the layered architecture
  (routes → services → ML/DB) does not block adding it later.
- The prediction-latency finding above (Section 4) is unresolved, not silently dropped.

## 6. Acceptance criteria (Milestone 10 checklist, pre-verified here)

- REST APIs are fully functional — verified via `TestClient` and a live `uvicorn` server
- Requests are validated correctly — 422 with structured field errors on invalid input
- Predictions are generated successfully, always with an explanation — no code path returns one
  without the other
- Explainability data is returned — both per-prediction and the precomputed global endpoint
- Errors are handled gracefully — categorized (validation/model/database/unexpected), consistent
  envelope, no leaked internals
- Logging is implemented — startup/shutdown/model-load/prediction/error events, no sensitive data
- Configuration is externalized — `Settings` (environment variables), `.env.example` documents them
- Database integration works — prediction history persists and is retrievable, via Alembic-managed
  schema
- API documentation is available and accurate — every endpoint has a summary, description, request/
  response examples, and documented error responses in the automatic OpenAPI docs
- The backend communicates with the ML subsystem only through `ML.explainability.service` and
  `ML.explainability.artifacts` — no ML training/preprocessing logic duplicated in `Backend/`
