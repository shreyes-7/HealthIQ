# Explainability API Preparation Report

Generated: 2026-07-25T10:01:58.279857+00:00

## Reusable Modules Built

- `ML/explainability/artifacts.py` — SHAP Loader (extended in this milestone with `load_shap_explainer`/`load_shap_expected_value`)
- `ML/explainability/service.py` — Explanation Generator (`ExplanationService.explain_patient`), Local Explanation Service (`ExplanationService.explain_by_split_row`), Global Explanation Service (`get_global_explanation`)
- `ML/explainability/export.py` — Visualization Export Utility (JSON + PNG)

## End-to-End Verification

- `ExplanationService()` loads model + pipeline + explainer + feature names **once**: 0.27s
- `explain_patient()` on a genuinely fresh raw row (never previously explained, loaded directly from the raw dataset, not from any split): 1.203s per call — this is the real latency the backend would see per request
  - Predicted P(admit): 0.0000
  - Top risk-increasing feature: `NUMDIS`
- `get_global_explanation()` served from Milestone 3's precomputed artifact (no recomputation): top feature `NUMDIS`

## Outputs

- JSON explanations: `ML/reports/explainability/api_check_example/explanation.json`, `global_explanation.json`
- PNG plots: `ML/reports/explainability/api_check_example/{waterfall,force,decision}_plot.png`

## Note for Backend Integration

`ExplanationService` should be instantiated **once** at backend process startup, not per request — `__init__` (artifact loading) is the fast, one-time cost (0.27s). `explain_patient()` is the part that runs per request, and at 1.20s it is borderline for a truly interactive API. Most of that time is the Sprint 1 cleaning pipeline's overhead (many pandas operations designed for bulk transformation, run here on a single row) rather than the SHAP computation itself, which is fast (see Milestone 2: 187 rows/sec in bulk). If sub-200ms single-request latency is required, profiling and optimizing the pipeline's single-row path — or batching requests — is worth a follow-up; flagged here rather than glossed over.