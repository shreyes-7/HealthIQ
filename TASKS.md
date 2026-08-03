# TASKS.md

# Sprint 4 - Backend Integration

Status: ✅ Complete

Owner: Backend Team

Goal:

Build the FastAPI backend that exposes the Sprint 2 production model (`ML/saved_models/model.pkl`) and the
Sprint 3 explainability layer (`ML/explainability/service.py`) as a versioned REST API, with request
validation, prediction history persistence, health monitoring, structured logging, and automated tests.

The backend must never train models, never recompute preprocessing logic independently of the Sprint 1
`PreprocessingPipeline`, and must never return a prediction without an accompanying explanation
(`CLAUDE.md`: "Explainability is a required feature. Not an optional enhancement.").

This sprint begins only after Sprint 3 (Explainable AI) and the Survey-Aware Deep Dive have been marked
complete.

---

# AI Agent Workflow

## Before Starting

1. Read `CLAUDE.md`.
2. Read this `TASKS.md`.
3. Inspect the repository, in particular `ML/explainability/service.py`, `ML/explainability/artifacts.py`,
   and `ML/saved_models/`.
4. Verify Sprint 2 and Sprint 3 artifacts exist (model, preprocessing pipeline, SHAP explainer, feature
   metadata).
5. Read `Docs/PROJECT_CONTEXT.md` sections 51–74 (Backend System) and 101–111 (Database System, API Design)
   only if additional information is required.

---

## While Working

1. Work through milestones in order, starting with the first incomplete one.
2. Never skip milestones.
3. Never train, retrain, or fit any model or preprocessing artifact from the backend — load only.
4. Reuse `ML/explainability/service.py` (`ExplanationService`, `get_global_explanation`) instead of
   reimplementing inference or SHAP logic inside `Backend/`.
5. Keep the ML, Backend, and Frontend boundaries intact — no cross-layer imports beyond the backend
   consuming `ML/` as a read-only dependency.
6. Keep implementations modular: routes call services, services call the ML layer and the database, nothing
   else.
7. Validate every request before it reaches the prediction/explanation engine.
8. Externalize all configuration (database URL, model paths, logging level, API version) via environment
   variables — never hardcode secrets or paths.
9. Document assumptions and limitations.
10. Continue automatically to the next milestone without waiting for approval.
11. Only stop if:
    - a blocker is encountered that cannot be resolved from the repository or documentation,
    - a required artifact is missing,
    - or completing the next step would require an unsupported design decision.

---

## Before Finishing (per milestone)

1. Verify milestone completion.
2. Run the backend test suite for the affected area.
3. Update milestone status in this file.
4. Continue to the next milestone immediately — do not stop or wait for review.

## Before Finishing (sprint)

Once every milestone is complete, summarize:
- Completed work
- Files created
- Endpoints exposed
- Key observations
- Limitations

Then stop and wait for review.

---

# Milestone 1 — Verify Artifacts & Scaffold Backend

## Objectives

Ensure all required ML assets exist before backend work begins, and lay out the backend project structure.

### Tasks

- [x] Verify `ML/saved_models/model.pkl`, `preprocessing_pipeline.pkl`, `shap_explainer.pkl`,
  `feature_names.json`, `model_metadata.json` all load successfully
- [x] Verify `ML/explainability/service.py` (`ExplanationService`) runs end-to-end on a sample raw record —
  used a genuinely fresh raw row (row 123), not a precomputed split row
- [x] Scaffold `Backend/app/` with `api/`, `core/`, `services/`, `schemas/`, `db/`, `models/`, `tests/`
- [x] Create the FastAPI application entrypoint
- [x] Add backend runtime dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic-settings`,
  `pytest`, `httpx`) to `requirements.txt` / `requirements-dev.txt`
- [x] Confirm the app starts locally and serves `/docs` — verified `/`, `/docs`, `/openapi.json` all return
  200

### Deliverables

- Backend Readiness Report — `Backend/reports/artifact_verification_report.md`
- Initial `Backend/app/` skeleton with a running FastAPI instance

Status

✅ Complete

---

# Milestone 2 — Configuration Management

## Objectives

Externalize all backend configuration.

### Tasks

- [x] Define a `Settings` object (environment-variable driven) for database URL, model artifact paths,
  logging level, application environment, and API version
- [x] Create `.env.example` documenting required variables without real values
- [x] Ensure no secrets, credentials, or file paths are hardcoded anywhere in `Backend/`
- [x] Support distinct configuration for development vs. production — `environment`/`debug` are
  environment-variable driven, `.env` is git-ignored

### Deliverables

- `Backend/app/core/config.py`
- `.env.example`
- `Backend/tests/test_config.py`

Status

✅ Complete

---

# Milestone 3 — Model & Explainability Service Layer

## Objectives

Give the backend a single, stateful integration point with the ML subsystem.

### Tasks

- [x] Wrap `ML.explainability.service.ExplanationService` in a backend service (`ExplanationRuntime`) that
  loads all artifacts once at application startup (FastAPI `lifespan`), not per request
- [x] Expose a service method for a single-patient prediction + explanation — `predict_and_explain()` adds
  risk-category and confidence-score business logic on top of the ML layer's raw explanation
- [x] Expose a service method for the precomputed global explanation
  (`ML.explainability.service.get_global_explanation`)
- [x] Verify model compatibility (feature schema, version) on startup; fail startup with a clear error if
  artifacts are missing or incompatible — `ModelCompatibilityError` compares `model.feature_name_` against
  `feature_names.json`, covered by a test that injects a mismatch
- [x] Ensure the backend never retrains, refits, or recomputes SHAP outside of what `ML/explainability`
  already provides — verified: `ExplanationRuntime` only calls `ExplanationService`/`get_global_explanation`

### Deliverables

- `Backend/app/services/prediction_service.py`
- `Backend/app/services/explanation_service.py`
- `Backend/app/main.py` — lifespan wiring
- `Backend/tests/test_explanation_service.py`, `test_prediction_service.py`, `test_main.py` (21 tests
  passing, full suite)

Status

✅ Complete

---

# Milestone 4 — Request/Response Schemas & Validation

## Objectives

Ensure no invalid or malformed data reaches the prediction engine.

### Tasks

- [x] Define a Pydantic request schema for a patient record covering the fields the
  `PreprocessingPipeline` expects — **design decision, confirmed with the user**: the pipeline's
  `transform()` requires all ~900 raw NHAMCS columns to be *present* (several cleaning steps index a
  fixed learned column list without an existence check — a genuinely missing column raises `KeyError`,
  not just a null value). Requiring a client to submit ~900 fields would violate the "simple form,
  minimal effort" product requirement, so the request schema exposes a curated ~18-field clinical
  subset (demographics, vitals, triage, arrival, and the Sprint 3 top-SHAP workup fields), and a new
  `Backend/app/services/patient_record_assembler.py` fills every other raw column with null before
  calling `transform()` — relying on the pipeline's own already-fitted median/"Missing"-category
  imputation, not new imputation logic. Verified empirically: a record with only the curated fields set
  produces all 866 expected model features with **zero NaNs**.
- [x] Added `ML/scripts/generate_raw_schema.py` → `ML/saved_models/raw_schema.json` (913 raw column
  names) so the backend never needs to load the raw SAS dataset at runtime to know the full column set
- [x] Validate required fields, data types, allowed value ranges, and reject unexpected fields
  (`extra="forbid"`)
- [x] Define response schemas: prediction outcome, admission probability, confidence score, risk category,
  explanation payload, model version, timestamp
- [x] Define a consistent error response schema (status, message, details, timestamp) — `SuccessResponse`/
  `ErrorResponse` envelope per `PROJECT_CONTEXT.md` §60/§110
- [x] Add unit tests for validation edge cases (missing fields, invalid categories, out-of-range values)

### Deliverables

- `Backend/app/schemas/patient.py`, `Backend/app/schemas/prediction.py`, `Backend/app/schemas/common.py`
- `Backend/app/services/patient_record_assembler.py`
- `ML/scripts/generate_raw_schema.py`, `ML/saved_models/raw_schema.json`
- `Backend/tests/test_patient_schema.py`, `test_prediction_schema.py`, `test_common_schema.py`,
  `test_patient_record_assembler.py` (47 tests passing, full suite)

Status

✅ Complete

Note: coded fields (`sex`, `race_ethnicity`, `triage_level`) are passed through as raw NHAMCS codebook
values rather than human-readable enums — the codebook layout file documents field names, not the
value-label tables, and guessing a Yes/No or category orientation wrong in a healthcare context was
judged riskier than shipping raw codes with descriptive `Field` docs. Flagged as future work once the
value-label tables are confirmed (likely a Frontend-sprint concern, since the frontend is what needs
human-readable choices).

---

# Milestone 5 — Prediction & Explainability API

## Objectives

Expose the core versioned REST endpoints.

### Tasks

- [x] `POST /api/v1/predict` — validate input, invoke the prediction service, return prediction +
  probability + confidence + risk category + explanation in one response (per `CLAUDE.md`, no prediction
  without explanation)
- [x] `GET /api/v1/explain/global` — return the precomputed global explanation
- [x] Routes contain no business logic — receive request, validate, call service, return response only
- [x] Return appropriate HTTP status codes for success (200), validation failure (422 — verified for
  missing required fields, out-of-range values, and unexpected fields)
- [x] Add API-level tests using `TestClient` / `httpx`
- [x] Live-verified with a running `uvicorn` server + `curl`, not just `TestClient` — both endpoints
  return correct, well-formed JSON

### Deliverables

- `Backend/app/api/v1/predict.py`, `Backend/app/api/v1/explain.py`, `Backend/app/api/v1/__init__.py`
  (aggregates the versioned router, mounted in `Backend/app/main.py` under `settings.api_prefix`)
- `Backend/app/schemas/explanation.py`
- `Backend/tests/test_predict_api.py`, `Backend/tests/test_explain_api.py` (54 tests passing, full suite)

Status

✅ Complete

---

# Milestone 6 — Database Integration & Prediction History

## Objectives

Persist operational data without touching the NHAMCS dataset or ML artifacts.

### Tasks

- [x] Define SQLAlchemy models for prediction history (prediction id, timestamp, model version,
  probability, outcome, confidence, processing time) — **scoped to match PROJECT_CONTEXT.md §64's field
  list exactly**: raw patient input (age/vitals/etc.) is deliberately NOT persisted, only the prediction
  outcome and an "explanation reference" (`top_contributing_features`, the top 3 increased/decreased-risk
  SHAP features as JSON), consistent with CLAUDE.md's "never log/store sensitive information"
- [x] Set up Alembic migrations — initialized under `Backend/alembic/` (kept inside `Backend/` rather
  than the repo root, so the backend subsystem stays self-contained); `env.py` reads the database URL from
  `Settings` (never hardcoded) and targets `Base.metadata`
- [x] Add a database session/connection layer, configurable via `Settings`
- [x] Persist a record on every successful `/api/v1/predict` call, in the service layer — not in the route
- [x] Add a read endpoint for prediction history (`GET /api/v1/predictions`, most-recent-first, limit
  configurable and capped)
- [x] Add database tests (using a test database/SQLite) — an isolated in-memory DB for `history_service`
  unit tests, plus a session-scoped fixture that runs `Base.metadata.create_all()` so the full suite is
  self-contained and doesn't depend on `alembic upgrade head` having been run manually first

### Deliverables

- `Backend/app/db/session.py`, `Backend/app/db/base.py`, `Backend/app/models/prediction.py`
- `Backend/alembic.ini`, `Backend/alembic/env.py`, `Backend/alembic/versions/*_create_prediction_history_table.py`
- `Backend/app/services/history_service.py`
- `Backend/app/schemas/history.py`, `Backend/app/api/v1/predictions.py`
- `Backend/tests/test_history.py`, `Backend/tests/test_predictions_api.py` (60 tests passing, full suite)

Status

✅ Complete

---

# Milestone 7 — Health Monitoring & Error Handling

## Objectives

Make the backend observable and fail gracefully.

### Tasks

- [x] `GET /health` — application liveness
- [x] `GET /health/model` — confirms model + explainer are loaded (503 `ModelUnavailableError` if not)
- [x] `GET /health/db` — confirms database connectivity (503 `DatabaseUnavailableError` if not)
- [x] Global exception handlers for validation errors, prediction errors, database errors, and unhandled
  errors — every error returns the common `ErrorResponse` envelope without leaking stack traces or
  internal paths. `RequestValidationError` (422), `AppError` subclasses (`ModelUnavailableError`,
  `DatabaseUnavailableError`, `PredictionError` — 503/500), `StarletteHTTPException` (404 etc.), and a
  catch-all `Exception` handler (500) all funnel through the same envelope
- [x] Tests covering each health endpoint and each error category — including simulated ML and database
  failures via monkeypatching, verified the response never contains "traceback" or an internal path

### Deliverables

- `Backend/app/api/health.py`
- `Backend/app/core/exceptions.py`
- `Backend/tests/test_health.py`, `Backend/tests/test_error_handling.py` (68 tests passing, full suite)

Status

✅ Complete

---

# Milestone 8 — Logging

## Objectives

Provide structured, non-sensitive logging.

### Tasks

- [x] Configure structured logging for application startup/shutdown, model loading, prediction requests,
  and errors — `configure_logging()`/`get_logger()` under a single `healthiq.backend` logger namespace,
  shared by `main.py`'s lifespan, `predict.py`'s request logging, and `core/exceptions.py`'s error logging
- [x] Ensure no patient-identifiable or sensitive data is logged — the prediction log line only records
  `model_version`, `risk_category`, `admission_probability`, and `processing_time_ms`; verified with a test
  that asserts submitted vitals (e.g. temperature, systolic BP) never appear in the log record
- [x] Make log level configurable via `Settings`

### Deliverables

- `Backend/app/core/logging.py`
- `Backend/tests/test_logging.py` (70 tests passing, full suite)

Status

✅ Complete

---

# Milestone 9 — API Documentation & Test Suite

## Objectives

Ensure the API is documented and verified end-to-end.

### Tasks

- [x] Add descriptions, request/response examples, and error response documentation to every endpoint for
  the automatic OpenAPI docs — summaries, descriptions, and `responses={...}` documenting the error
  envelope added to every route; example payloads added to `PatientRecordRequest`/`PredictionResponse`
- [x] Run the full backend `pytest` suite (unit, schema, API, database, health) and confirm all pass —
  **70/70 passing**
- [x] Run one genuinely fresh raw patient record through `POST /api/v1/predict` against the running app to
  confirm the live path works end-to-end, not just the test suite — row 15428 of the raw dataset, selected
  programmatically (filtered to non-sentinel values), never used by any prior milestone/test; verified
  live against a running `uvicorn` server, including that the prediction was persisted and retrievable via
  `GET /api/v1/predictions`
- [x] Document any latency or performance limitations (see Sprint 3 Milestone 8's ~1.2s explanation latency
  note) in the backend readiness report — **finding**: measured latency this sprint is consistently
  ~2.3-2.6s, roughly double Sprint 3's figure. Root-caused as far as this sprint's scope allows: verified
  the curated-subset/auto-fill design is NOT the cause (a fully-populated real row is exactly as slow as
  the mostly-null assembled row, and the regression reproduces in a single call in a fresh process).
  Flagged as an open follow-up for the ML subsystem, not silently dropped and not fixed here since
  root-causing SHAP/LightGBM performance is outside this sprint's backend-only scope.

### Deliverables

- `Backend/reports/backend_readiness_report.md`
- Full `Backend/tests/` suite passing (70/70)

Status

✅ Complete

---

# Milestone 10 — Ready for Frontend Integration

Sprint 4 is complete when:

- [x] REST APIs are fully functional — `/predict`, `/explain/global`, `/predictions`, `/health*`, live- and
  test-verified
- [x] Requests are validated correctly — 422 on missing/invalid/unexpected fields
- [x] Predictions are generated successfully, always with an explanation — single response shape, no
  prediction-only path exists
- [x] Explainability data is returned — per-prediction (SHAP) and global (precomputed)
- [x] Errors are handled gracefully — categorized, common envelope, no leaked internals
- [x] Logging is implemented — startup/shutdown/model-load/prediction/error, no sensitive data
- [x] Configuration is externalized — `Settings` + `.env.example`, nothing hardcoded
- [x] Database integration works (prediction history persists and is retrievable) — Alembic-managed
  schema, verified via a live round trip
- [x] API documentation is available and accurate — OpenAPI summaries/descriptions/examples on every
  endpoint
- [x] The backend can communicate with the ML subsystem without direct coupling, and is ready for the
  Frontend to consume it — only touches `ML.explainability.service`/`ML.explainability.artifacts`, never
  ML training/preprocessing internals directly

All 10 checks pass. See `Backend/reports/backend_readiness_report.md`.

Status

✅ READY — Sprint 4 is complete.

---

# Sprint Deliverables

```
Backend/
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/*_create_prediction_history_table.py
├── app/
│   ├── api/
│   │   ├── health.py                  (Milestone 7)
│   │   └── v1/
│   │       ├── __init__.py             (aggregates the versioned router)
│   │       ├── predict.py
│   │       ├── explain.py
│   │       └── predictions.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py                 (Milestone 8)
│   │   └── exceptions.py              (Milestone 7)
│   ├── services/
│   │   ├── prediction_service.py
│   │   ├── explanation_service.py
│   │   ├── patient_record_assembler.py
│   │   └── history_service.py
│   ├── schemas/
│   │   ├── patient.py
│   │   ├── prediction.py
│   │   ├── explanation.py
│   │   ├── history.py
│   │   └── common.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   └── prediction.py
│   └── main.py
├── tests/
└── reports/
    ├── artifact_verification_report.md   (Milestone 1)
    └── backend_readiness_report.md        (Milestone 9)
```

ML/ additions supporting the backend (Sprint 4, not Sprint 3):

```
ML/scripts/generate_raw_schema.py
ML/saved_models/raw_schema.json
```

Generated Artifacts

- FastAPI application (versioned `/api/v1` routes)
- Prediction + Explanation endpoint, with a curated-subset request schema and full-raw-record
  assembler (`PatientRecordAssembler`)
- Database schema + Alembic migrations for prediction history
- Health monitoring endpoints (liveness, model, database)
- Structured logging (no sensitive data)
- Categorized error handling with a consistent response envelope
- Backend test suite (70/70 passing)
- Backend Readiness Report + Artifact Verification Report

---

# Sprint Status

**Progress: 10/10 milestones complete. Sprint 4 (Backend Integration) is DONE.**

The backend serves the Sprint 2 production model and Sprint 3 explainability layer end-to-end:
patient record in → validated → assembled into the full raw schema → `PreprocessingPipeline` →
model → SHAP → prediction + explanation out → persisted to prediction history — verified live
against a running server with a genuinely fresh raw dataset row (row 15428), not just the test
suite. One design fork was surfaced and resolved with the user rather than guessed (Milestone 4):
the pipeline's hard requirement for all ~900 raw columns to be present led to a curated ~18-field
request schema plus a full-record assembler, instead of either exposing all raw columns or
silently under-scoping the API. One open issue was found and documented, not silently dropped:
per-prediction latency measured this sprint (~2.3-2.6s) is roughly double Sprint 3's reported
figure, root-caused as far as backend-only scope allows (confirmed NOT caused by the
curated-subset design) and flagged as ML-subsystem follow-up work.

Current Task:

Sprint 4 is complete. Ready for Sprint 5 (Frontend Integration) — awaiting instruction to begin.
