# Milestone 1 — Artifact Verification & Backend Scaffolding Report

Sprint 4 (Backend Integration) — Milestone 1

---

## 1. Artifact Verification

All Sprint 2/3 artifacts required for the backend were loaded directly (no retraining, no
recomputation) and verified to work end-to-end.

| Artifact | Path | Result |
|---|---|---|
| Production model | `ML/saved_models/model.pkl` | Loads as `LGBMClassifier` |
| Model metadata | `ML/saved_models/model_metadata.json` | version `1.0.0`, model `lightgbm` |
| Feature names | `ML/saved_models/feature_names.json` | 866 features |
| Preprocessing pipeline | `ML/saved_models/preprocessing_pipeline.pkl` | Loads as `PreprocessingPipeline` |
| SHAP explainer | `ML/saved_models/shap_explainer.pkl` | Loads as `TreeExplainer`, expected value -8.3047 |

## 2. End-to-End Explanation Service Check

`ML.explainability.service.ExplanationService` was exercised against a genuinely fresh raw
patient record (row 123 of the raw NHAMCS dataset, loaded via `ML.ingestion.loader.load_dataset`
— not a row from any precomputed split or earlier milestone artifact).

- Service initialization (loads model, pipeline, explainer, feature names, expected value once):
  **0.331s**
- `explain_patient()` on the fresh raw row (raw → `PreprocessingPipeline` → model → SHAP →
  plain-language explanation): **1.396s**
- Result keys: `predicted_probability`, `base_rate_probability`, `predicted_admission`,
  `features_that_increased_risk`, `features_that_decreased_risk`
- `get_global_explanation(top_n=5)` (serves Sprint 3 Milestone 3's precomputed artifact, no SHAP
  recomputation): **0.04s**

This confirms the same latency profile already flagged in Sprint 3 Milestones 8/9 (~1.2-1.4s per
fresh-record explanation, driven by the cleaning pipeline's per-row overhead rather than SHAP
itself). No new bottleneck was introduced by this check; it is re-flagged here as a backend
concern to revisit in Milestone 9 if sub-200ms latency becomes a requirement.

## 3. Backend Scaffolding

`Backend/app/` was created with the layered structure specified in `TASKS.md`:

```
Backend/
├── __init__.py
├── app/
│   ├── __init__.py
│   ├── main.py          (FastAPI app instance)
│   ├── api/
│   │   └── v1/           (routers added in Milestone 5)
│   ├── core/             (config/logging/exceptions added in Milestones 2, 7, 8)
│   ├── services/         (prediction/explanation/history services added in Milestones 3, 6)
│   ├── schemas/          (request/response models added in Milestone 4)
│   ├── db/               (session management added in Milestone 6)
│   └── models/           (SQLAlchemy models added in Milestone 6)
├── tests/
└── reports/
```

Only `app/main.py` contains executable logic at this milestone — a minimal `FastAPI()` instance
with a root health-check-style endpoint, deliberately scoped to confirm the application boots and
serves documentation. Configuration, the ML service layer, request validation, and the actual
prediction/explanation routes are out of scope for this milestone (Milestones 2-7).

## 4. Dependencies

Added to `requirements.txt` (runtime): `fastapi`, `uvicorn[standard]`, `pydantic-settings`,
`sqlalchemy`, `alembic`.

Added to `requirements-dev.txt` (testing): `httpx` (required by FastAPI's `TestClient`).

Installed into the existing repository `.venv` — no global installs.

## 5. Application Boot Verification

Started with `uvicorn Backend.app.main:app` and checked with `curl`:

| Endpoint | Status |
|---|---|
| `GET /` | 200 — `{"service": "HealthIQ Backend API", "status": "running"}` |
| `GET /docs` | 200 |
| `GET /openapi.json` | 200 |

Server was stopped after verification.

## 6. Limitations

- No configuration, logging, database, or ML-service wiring exists yet — those are explicitly
  Milestones 2, 3, 6, 7, 8.
- The 1.3-1.4s fresh-record explanation latency is carried over unchanged from Sprint 3; it has
  not yet been addressed and will inform Milestone 9's documentation, not this one.

---

**Milestone 1 status: complete.** All artifacts verified, backend scaffold created, application
confirmed to boot and serve documentation.
