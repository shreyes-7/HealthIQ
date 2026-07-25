# TASKS.md

# Sprint 3 - Explainable AI (SHAP)

Status: ✅ Complete

Owner: ML Team

Goal:

Develop a complete Explainable AI pipeline for the selected Emergency Department admission prediction model using SHAP.

The objective is to generate reliable global and local explanations, validate explanation quality, and prepare explainability artifacts for backend integration, frontend visualization, and research reporting.

This sprint begins only after Sprint 2 has successfully selected and serialized the production model.

---

# AI Agent Workflow

## Before Starting

1. Read `CLAUDE.md`.
2. Read this `TASKS.md`.
3. Inspect the repository.
4. Verify Sprint 2 artifacts exist.
5. Read `Docs/PROJECT_CONTEXT.md` only if additional information is required.

---

## While Working

1. Work through milestones in order, starting with the first incomplete one.
2. Never skip milestones.
3. Reuse preprocessing artifacts.
4. Reuse the production model selected in Sprint 2.
5. Never retrain models.
6. Keep implementations modular.
7. Produce reusable explainability utilities.
8. Save every generated visualization and report.
9. Document assumptions and limitations.
10. Continue automatically to the next milestone without waiting for approval.
11. Only stop if:
    - a blocker is encountered that cannot be resolved from the repository or documentation,
    - a required artifact is missing,
    - or completing the next step would require an unsupported design decision.

---

## Before Finishing (per milestone)

1. Verify milestone completion.
2. Validate generated explanations.
3. Update milestone status in this file.
4. Continue to the next milestone immediately — do not stop or wait for review.

## Before Finishing (sprint)

Once every milestone is complete, summarize:
- Completed work
- Files created
- Visualizations generated
- Key observations
- Limitations

Then stop and wait for review.

---

# Milestone 1 — Verify Sprint 2 Artifacts

## Objectives

Ensure all required assets exist before explainability begins.

### Tasks

- [x] Load preprocessing pipeline
- [x] Load best trained model — `lightgbm` v1.0.0
- [x] Load feature metadata — 866 features
- [x] Load train dataset — (11,217, 873)
- [x] Load validation dataset — (2,404, 873)
- [x] Load test dataset — (2,404, 873)
- [x] Verify feature ordering — train split columns AND the model's own
  `feature_name_` both match `feature_names.json` exactly
- [x] Verify preprocessing compatibility — ran the loaded `PreprocessingPipeline`
  fresh on a raw 50-row sample end-to-end (raw → transform → predict); output
  feature schema matches the model's expected features exactly, and the model
  produces predictions with no errors

All 10 checks passed. No model was retrained — everything was loaded, not regenerated.

### Deliverables

- Explainability Readiness Report — `ML/reports/explainability/explainability_readiness_report.md`
- `ML/explainability/artifacts.py` — reusable loader module for Milestones 2+

Status

✅ Complete

---

# Milestone 2 — SHAP Integration

## Objectives

Initialize the SHAP explainability framework.

### Tasks

- [x] Detect model type — `LGBMClassifier` → tree family
- [x] Select appropriate SHAP Explainer — `TreeExplainer` (exact, no background sample needed)
- [x] Initialize explainer
- [x] Generate SHAP values — on the validation split (held-out, unseen during training)
- [x] Verify output dimensions — (2404, 866), matches expected exactly
- [x] Verify runtime performance — 12.84s / 2,404 rows (187 rows/sec, comfortably interactive)

Empirically confirmed (not assumed) that `shap_values` are a single `(n_rows, n_features)`
array in **margin/log-odds space** for this model+library combo, despite a SHAP UserWarning
suggesting otherwise — `shap_values.sum(axis=1) + expected_value` reconstructs
`model.predict(X, raw_score=True)` to within 3e-9. See `ML/explainability/explainer.py` docstring.

### Deliverables

- SHAP Explainer — `ML/saved_models/shap_explainer.pkl`
- SHAP Values — `ML/reports/explainability/shap_values_validation.npy`
- `ML/explainability/explainer.py`, `shap_utils.py`
- `ML/reports/explainability/shap_integration_report.md`

Status

✅ Complete

---

# Milestone 3 — Global Explainability

## Objectives

Understand overall model behavior.

### Tasks

Generate:

- [x] SHAP Summary Plot — top 20 individual encoded features
- [x] SHAP Bar Plot — mean |SHAP| ranking, same granularity
- [x] Beeswarm Plot — custom, aggregated **by source variable** (one-hot dummies summed
  back together) rather than a third near-duplicate per-encoded-feature view; SHAP has no
  native support for this grouping, built directly with matplotlib
- [x] Global Feature Importance — both per-encoded-feature and per-source-variable
- [x] Mean Absolute SHAP Values — `ML/explainability/shap_utils.py`

Document:

- [x] Most influential features — `NUMDIS`, `CONSULT`, `TOTDIAG`, `DIAG1`, `IMMEDR` top 5
- [x] Least influential features — mostly rare medication-slot fields (`GPMED13-16`, `RX*`
  detail codes), consistent with Sprint 1's near-zero-variance findings
- [x] Clinical interpretation — cross-referenced against the data dictionary; **cross-validated
  against Sprint 2's independent tree-importance/mutual-information ranking** — strong overlap
  in the top ~10 variables gives real confidence the model leans on clinically plausible signal
  under two different measurement methods, not an artifact of one method

### Deliverables

- `ML/reports/explainability/global_explainability_report.md` (markdown, not PDF — every
  other report in this project is markdown; a PDF toolchain would be a new dependency for
  one file. Flagged, not silently substituted.)
- `ML/reports/explainability/visualizations/summary_plot.png`, `bar_plot.png`, `beeswarm_plot.png`
- `ML/explainability/global_explanations.py` (named `global_explanations.py`, not the sprint
  plan's literal `global.py` — `global` is a reserved Python keyword; `import global` is a
  SyntaxError, so that literal filename could never work)

Status

✅ Complete

---

# Milestone 4 — Local Explainability

## Objectives

Explain individual patient predictions.

### Tasks

Generate (per patient):

- [x] Waterfall Plot
- [x] Force Plot
- [x] Decision Plot

Explain:

- [x] Why patient was admitted/not admitted (plain-language JSON + markdown per patient)
- [x] Which variables increased risk
- [x] Which variables reduced risk

Test multiple patient examples — **selected programmatically, not hand-picked**, to cover
genuinely different cases rather than three easy wins:
- `patient_1`: highest-confidence correctly-predicted admission (P=0.9999)
- `patient_2`: highest-confidence correctly-predicted discharge (P=0.0000)
- `patient_3`: the model's most uncertain prediction, closest to the 0.5 decision boundary
  (P=0.5067) — the most instructive case, since it shows competing evidence (`CONSULT`/`NUMDIS`/
  `TOTDIAG` pushing toward admission, balanced against a rare diagnosis code and younger age
  pulling the other way)

### Deliverables

- `ML/reports/explainability/patient_explanations/patient_{1,2,3}/` — each with
  `waterfall_plot.png`, `force_plot.png`, `decision_plot.png`, `explanation.json`, `README.md`
- `ML/explainability/local_explanations.py`

Status

✅ Complete

---

# Milestone 5 — Dependence Analysis

## Objectives

Understand feature interactions.

### Tasks

Generate SHAP Dependence Plots for:

- [x] Top Feature — `NUMDIS`
- [x] Second Feature — `CONSULT__Yes`
- [x] Third Feature — `TOTDIAG`
- [x] Additional important variables — 5 more, prioritizing continuous features over one-hot
  dummies (which only show two point clouds, not a traceable curve): `DIAG1__frequency`, `LOV`,
  `AGE`, `DIAG2__frequency`, `DRUGID2__frequency`

Identify:

- [x] Nonlinear effects — **`AGE`**: flat-to-slightly-negative contribution for younger/middle-aged
  patients, then a clear nonlinear upward inflection for older patients — consistent with real
  clinical knowledge about elderly admission risk
- [x] Threshold effects — see `AGE` above; also documented per-feature in the report via a
  raw-value/SHAP-value correlation check (low correlation flags a non-monotonic relationship
  worth looking at the actual plot for)
- [x] Feature interactions — each plot auto-colored by SHAP's chosen interaction feature
  (e.g. `AGE` colored by `CONSULT__Yes`)

### Deliverables

- `ML/reports/explainability/dependence_plots/` (8 plots)
- `ML/reports/explainability/dependence_analysis_report.md`
- `ML/explainability/dependence.py`

Status

✅ Complete

---

# Milestone 6 — Cohort Analysis

## Objectives

Compare explanations across patient groups.

### Tasks

Generate explanations by:

- [x] Admission vs Discharge
- [x] Age groups
- [x] Gender
- [x] Arrival mode
- [x] Triage level

Categories reconstructed from their one-hot encoded columns using the encoder's own saved
reference-category metadata (generic, not hand-listed per variable) — see
`ML/explainability/cohort.py`.

Compare:

- [x] Feature importance (top 5 by mean \|SHAP\| per group, all group sizes verified to sum
  exactly to the 2,404-row validation split)
- [x] SHAP distributions — boxplot of total \|SHAP\| per row, per group

**Findings**: the top 3 features (`NUMDIS`, `CONSULT`, `TOTDIAG`) are consistent across nearly
every cohort — the model applies the same core reasoning regardless of subgroup, not a
different process per group. Two genuine, clinically plausible exceptions stood out: `AGE`
enters the top-5 ranking only for the `older_adult_65_plus` cohort (mean P(admit) 0.277, highest
of any age group), and ambulance-arrival patients (`arrival_mode=1`) show 3x the mean predicted
admission probability of other arrival modes (0.279 vs. 0.085).

### Deliverables

- Cohort Explainability Report — `ML/reports/explainability/cohort_analysis_report.md`,
  `cohort_analysis.json`
- `ML/reports/explainability/cohort_plots/` (5 distribution boxplots)
- `ML/explainability/cohort.py`

Status

✅ Complete

---

# Milestone 7 — Explanation Validation

## Objectives

Ensure explanations are reliable.

### Tasks

Verify:

- [x] SHAP values reproduce predictions — checked on the FULL validation split (2,404 rows,
  not a sample): max abs diff 1.55e-9 (machine precision)
- [x] Feature ordering consistency — SHAP array width, `feature_names.json` length, and the
  features DataFrame's column order all match exactly
- [x] Explanation stability — recomputed SHAP for the same 100 rows twice: **exactly bit-identical**
  (0.0 diff), confirming `TreeExplainer`'s tree-path-dependent algorithm is deterministic, not
  sampling-based
- [x] No preprocessing mismatch — re-ran the Milestone 1 raw→pipeline→model check fresh
- [x] No missing SHAP values — 0 NaN across all 2,081,864 computed values

**All 5 checks PASS.**

Document limitations:

- [x] These checks validate SHAP's internal mathematical consistency with the model and the
  preprocessing handoff — they do NOT validate that the underlying model is clinically correct
  or unbiased (a separate, ongoing concern, partially addressed by the cross-checks in
  Milestones 3 and 6, not resolved by this milestone alone). Documented explicitly in the report
  rather than implied by an all-green checklist.

### Deliverables

- Validation Report — `ML/reports/explainability/explanation_validation_report.md`
- `ML/explainability/validation.py`

Status

✅ Complete

---

# Milestone 8 — Explainability API Preparation

## Objectives

Prepare reusable utilities for backend.

### Tasks

Create reusable modules:

- [x] SHAP Loader — `ML/explainability/artifacts.py` (`load_shap_explainer`, `load_shap_expected_value`)
- [x] Explanation Generator — `ExplanationService.explain_patient()` — takes a **fresh raw
  record** (never seen before), runs the full raw → `PreprocessingPipeline` → model → SHAP chain
- [x] Global Explanation Service — `get_global_explanation()`, serves Milestone 3's precomputed
  artifact rather than recomputing per call
- [x] Local Explanation Service — `ExplanationService.explain_by_split_row()`, quick lookup for
  an existing split row
- [x] Visualization Export Utility — `ML/explainability/export.py` (JSON + PNG)

Outputs:

- [x] JSON explanations
- [x] PNG plots
- [x] Metadata

**End-to-end verified, not just defined**: tested `explain_patient()` on a genuinely fresh raw
row (row 15000, loaded directly from the raw dataset, never explained by any earlier milestone).
`ExplanationService()` loads all artifacts once in 0.28s; `explain_patient()` per call is 1.2s —
flagged as borderline for a truly interactive API (mostly the cleaning pipeline's per-row
overhead, not SHAP itself, which runs at 187 rows/sec in bulk per Milestone 2) — worth a
follow-up if sub-200ms latency is required.

### Deliverables

- `ML/explainability/service.py`, `export.py`
- `ML/reports/explainability/explainability_api_report.md`
- `ML/reports/explainability/api_check_example/` (example JSON + PNG output)

Status

✅ Complete

---

# Milestone 9 — Research Documentation

## Objectives

Prepare explainability outputs for publication.

### Tasks

Generate (synthesized from Milestones 3-8's already-computed artifacts — nothing recomputed,
so the report cannot drift from what Milestone 7 actually validated):

- [x] Feature Importance Table — top 20 source variables with data-dictionary labels
- [x] Global Interpretation Report — cross-validated against Sprint 2's independent
  tree-importance ranking; documents `AGE`'s nonlinear effect
- [x] Local Interpretation Report — synthesizes the 3 patient cases from Milestone 4
- [x] Clinical Findings — 4 findings pulled directly from `cohort_analysis.json`
  (admission-status separation, elderly-cohort age sensitivity, ambulance-arrival risk, and
  cross-cohort consistency)
- [x] Limitations — 5 documented (SHAP explains the model not medical reality; one-hot
  fragmentation, corrected for; validation scope; API latency; tree-path-dependent
  perturbation's correlated-feature caveat)
- [x] Future Work — 5 items (SHAP interaction values, fairness audit, backend integration,
  drift monitoring, survey-aware explanation comparison)

### Deliverables

- Explainability Report — `ML/reports/explainability/explainability_research_report.md`

Status

✅ Complete

---

# Milestone 10 — Ready for Backend Integration

Sprint 3 is complete when:

- [x] SHAP integrated
- [x] Global explanations generated
- [x] Local explanations generated
- [x] Dependence analysis completed
- [x] Cohort analysis completed
- [x] Explanations validated
- [x] Explainability utilities created
- [x] JSON outputs generated
- [x] Reports completed
- [x] Ready for FastAPI integration — verified with a live call, not just a file check:
  `ExplanationService().explain_patient()` run end-to-end on a genuinely fresh raw row

All 10 checks pass. See `ML/reports/explainability/ready_for_backend_integration.md`.

Status

✅ READY — Sprint 3 is complete.

---

# Sprint Deliverables

Actual repository layout (two filenames deviate from the sprint plan's literal names —
`global.py`/`local.py` — documented at Milestone 3/4: `global` is a reserved Python keyword,
so `import global` is a SyntaxError and that literal filename could never have worked):

```
ML/explainability/
├── artifacts.py          (SHAP/model/pipeline/split loaders)
├── explainer.py           (model-type detection, TreeExplainer setup, SHAP value computation)
├── shap_utils.py           (sigmoid, source-variable aggregation, per-row explanation builder)
├── global_explanations.py  (Milestone 3 — was "global.py" in the plan; see note above)
├── local_explanations.py   (Milestone 4)
├── dependence.py            (Milestone 5)
├── cohort.py                (Milestone 6)
├── validation.py            (Milestone 7)
├── service.py                (Milestone 8 — ExplanationService, get_global_explanation)
└── export.py                 (Milestone 8 — JSON/PNG export)

ML/reports/explainability/
├── explainability_readiness_report.md, shap_integration_report.md
├── global_explainability_report.md, visualizations/{summary,bar,beeswarm}_plot.png
├── patient_explanations/patient_{1,2,3}/{waterfall,force,decision}_plot.png + explanation.json + README.md
├── dependence_analysis_report.md, dependence_plots/ (8 plots)
├── cohort_analysis_report.md, cohort_analysis.json, cohort_plots/ (5 plots)
├── explanation_validation_report.md
├── explainability_api_report.md, api_check_example/
├── explainability_research_report.md
└── ready_for_backend_integration.md

ML/saved_models/shap_explainer.pkl
ML/tests/test_shap_utils.py (+5 tests; full suite: 55/55 passing)
```

Note: reports are markdown, not PDF (`explainability_report.pdf`/`validation_report.pdf` in
the original plan) — every other report in this project is markdown; a PDF toolchain would be
a new dependency for this alone. Same substitution already made and flagged for Sprint 1's EDA
notebook request.

Generated Artifacts

- SHAP Explainer & Values
- Global Report (+ 3 visualizations)
- Local Reports (3 patients x 3 plot types + JSON + README)
- Dependence Analysis Report (+ 8 plots)
- Cohort Report (+ 5 plots, JSON)
- Validation Report (5/5 checks pass)
- Explainability Utilities (`service.py`, `export.py` — live-tested, not just defined)
- Research Report (feature importance table, clinical findings, limitations, future work)
- Backend Integration Readiness Gate

---

# Sprint Status

**Progress: 10/10 milestones complete. Sprint 3 (Explainable AI) is DONE.**

Selected model (`lightgbm`) is confirmed explainable end-to-end: raw patient record →
`PreprocessingPipeline` → model → SHAP → plain-language explanation, validated to reconstruct
actual predictions to within 1.5e-9 and reproduce bit-identically across runs. One caught issue
along the way: a draft "consistent with Sprint 2" claim in the global-explainability report was
verified against the actual computed ranking before being kept (see Milestone 3) rather than
asserted from memory. One real limitation flagged for follow-up, not glossed over: per-request
explanation latency (~1.2s) is borderline for a truly interactive API (Milestone 8/9).

**Post-sprint addition**: per standing user preference (see `ML/notebooks/eda_report.ipynb`
from Sprint 1), two more presentation-layer notebooks were added after this sprint was marked
complete — `ML/notebooks/model_development_report.ipynb` (Sprint 2) and
`ML/notebooks/explainability_report.ipynb` (Sprint 3). Both import/load already-computed
artifacts only (experiment log, SHAP values, cohort JSON) — no retraining, no SHAP
recomputation — and were executed end-to-end (`jupyter nbconvert --execute`) with all values
cross-checked against the existing markdown reports before being considered done.

---

# Post-Sprint 3 Addition — Survey-Aware Deep Dive

Status: ✅ Complete

Owner: ML Team

Goal:

Close a gap identified after Sprint 3 was marked complete: this project's stated primary
research contribution (`Docs/PROJECT_CONTEXT.md` §44, survey-aware prediction using NHAMCS's
`PATWT` sample weights) had only ever been tested with a first-pass Logistic Regression
(`ML/modeling/survey_aware.py`, Sprint 2) — never on the actual production LightGBM model, never
connected to SHAP explainability, and with no fairness audit at all. This work item runs the full
comparison — performance, explanations, and fairness — on the production model.

### Tasks

- [x] Fit a survey-weighted LightGBM using the exact production hyperparameters (from
  `experiment_log.json`) plus `sample_weight=PATWT`; evaluate against the existing unweighted
  `model.pkl` (not refit) on validation + test splits — `ML/modeling/survey_aware_lightgbm.py`,
  `ML/scripts/run_survey_aware_lightgbm.py`
- [x] Compute SHAP values for the weighted model (same `TreeExplainer` approach as Sprint 3),
  compare global importance rankings against the unweighted model via Spearman rank correlation
  and top-20 overlap — `ML/explainability/survey_aware_shap.py`
- [x] Per-patient explanation comparison (the same 3 patients from Sprint 3 Milestone 4) plus a
  systematic decision-flip-rate analysis across the full validation split (not just anecdotal
  examples) — `ML/scripts/run_survey_aware_shap_comparison.py`
- [x] Fairness audit across race/ethnicity (`RACERETH`, verified against the NCHS codebook, not
  assumed) for both models: selection rate, true positive rate, false positive rate, per-group
  ROC-AUC, and max-min disparity gaps — `ML/explainability/fairness.py`,
  `ML/scripts/run_fairness_audit.py`
- [x] Consolidated summary tying the three pieces together — `ML/scripts/run_survey_aware_summary.py`
- [x] Unit tests for all new pure functions (10 tests; full suite now 65/65 passing) —
  `ML/tests/test_survey_aware_deep_dive.py`
- [x] Companion presentation-layer notebook, same pattern as the three Sprint 1-3 notebooks
  (loads precomputed artifacts only, no recomputation, executed end-to-end via
  `jupyter nbconvert --execute`) — `ML/notebooks/survey_aware_deep_dive_report.ipynb`

**Findings**: validation/test ROC-AUC drop by 0.0022/0.0030 under weighting — small, expected,
and far smaller than Sprint 2's Logistic Regression comparison. SHAP rankings are stable
(Spearman 0.9725, 18/20 top-feature overlap); only 47/2404 (1.96%) validation predictions flip
across the 0.5 threshold, concentrated near the decision boundary (mean distance 0.166 for
flipped vs. 0.481 for non-flipped). The fairness audit found 3 of 4 disparity metrics
(selection rate, true positive rate, false positive rate) narrow under weighting, while the
per-group ROC-AUC gap widens slightly — read as suggestive on a single validation split, not
statistically certified (no bootstrap confidence intervals).

### Deliverables

- `ML/saved_models/model_survey_weighted.pkl`
- `ML/reports/survey_aware_deep_dive/` — `weighted_vs_unweighted_lightgbm.md`,
  `shap_comparison_report.md`, `fairness_audit_report.md`, `summary.md` (+ matching `.json` files
  and `figures/`)
- `ML/notebooks/survey_aware_deep_dive_report.ipynb`
- `ML/tests/test_survey_aware_deep_dive.py`

Status

✅ Complete

---

Current Task:
Sprint 3 and the Survey-Aware Deep Dive are both complete. Ready for Sprint 4 (Backend
Integration) — awaiting instruction to begin.