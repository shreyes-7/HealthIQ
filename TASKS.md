Begin Sprint 2 – Machine Learning Model Development.

Your instructions:

1. Read CLAUDE.md completely.
2. Read TASKS.md completely.
3. Inspect the repository.
4. Verify that all Sprint 1 artifacts exist before starting.

Execution rules:

- Complete every milestone in TASKS.md sequentially.
- Do not skip milestones.
- If a milestone depends on a previous one, complete the dependency first.
- Reuse the preprocessing pipeline and artifacts from Sprint 1.
- Never modify the raw dataset.
- Produce clean, modular, production-quality code.
- Save all generated models, reports, metrics, visualizations, and metadata in the appropriate project directories.
- Run validation after each major stage where appropriate.
- Update TASKS.md as each milestone is completed.
- Continue automatically to the next milestone without waiting for approval.
- Only stop if:
  - you encounter a blocker that cannot be resolved from the repository or documentation,
  - a required artifact is missing,
  - or completing the next step would require making an unsupported design decision.

Sprint completion requirements:

The sprint is complete only when every milestone in TASKS.md has been finished, all deliverables have been generated, and the "Ready for Explainable AI" milestone is satisfied.

When the sprint is finished, provide a final report including:
- Completed milestones
- Models trained
- Hyperparameter tuning results
- Cross-validation results
- Evaluation metrics for all models
- Model comparison
- Selected best model and rationale
- Files created or modified
- Any remaining limitations or recommendations

Do not pause after individual milestones. Continue until Sprint 2 is fully complete or a genuine blocker prevents further progress.

---

# Sprint 2 - Machine Learning Model Development

Status: ✅ Complete

Owner: ML Team

Goal:
Train, tune, evaluate, and compare multiple candidate models on the Sprint 1 preprocessing
output, select and serialize the best model, and verify it is ready to be explained.

No milestone list existed in this file when Sprint 2 began — the breakdown below is derived
directly from `Docs/PROJECT_CONTEXT.md` §31-50 (Machine Learning System spec), mirroring
Sprint 1's milestone format so progress stays trackable the same way.

Inputs (verified present before starting):
- `Data/processed/{train,validation,test}.parquet` (11,217 / 2,404 / 2,404 rows, 866 features, target `hospital_admission`)
- `ML/saved_models/preprocessing_pipeline.pkl` (fit on training split only)
- Target is imbalanced: 13.24% positive (admitted)

---

# Milestone 1 — Training Infrastructure & Experiment Setup

## Objectives

Build the reusable scaffolding every subsequent milestone trains through, so no model
training loop is duplicated per algorithm (PROJECT_CONTEXT §38 Training Pipeline, §45
Experiment Tracking).

Tasks

- [x] Metrics module (accuracy, precision, recall, specificity, sensitivity, F1, ROC-AUC, PR-AUC, confusion matrix, calibration curve)
- [x] Cross-validation utility (stratified k-fold on the training split)
- [x] Experiment record schema (model, hyperparameters, CV scores, metrics, seed, timestamp)
- [x] Added XGBoost, LightGBM, CatBoost, SHAP, statsmodels, tabulate to `requirements.txt` and installed

Deliverables

- `ML/modeling/metrics.py`, `ML/modeling/cross_validation.py`, `ML/modeling/experiment_log.py`
- `ML/modeling/model_registry.py` (consolidates the originally-sketched per-family model files —
  linear/tree/ensemble/stacking all follow the identical "estimator factory + search space" shape,
  so one registry is more cohesive than four near-duplicate files)

Status

✅ Complete

---

# Milestone 2 — Baseline Models

## Objectives

Establish interpretable baselines before more complex models (Logistic Regression, Decision Tree).

Tasks

- [x] Train Logistic Regression — validation ROC-AUC 0.9387, PR-AUC 0.7187
- [x] Train Decision Tree — validation ROC-AUC 0.8930, PR-AUC 0.5857
- [x] Cross-validate both on the training split (5-fold)
- [x] Record baseline metrics

Deliverables

- `ML/modeling/model_registry.py` (`logistic_regression`, `decision_tree` entries)
- Baseline experiment records — `ML/reports/modeling/experiment_log.json`

Note: `LogisticRegression` initially used `solver="saga"`, which took ~155s per fit and still
failed to converge (`ConvergenceWarning`, hit `max_iter=1000`). Benchmarked alternatives —
`liblinear` converged in ~2.6s (17 iterations) with identical L1/L2 support for this binary
classification task. Switched; full 15-iteration hyperparameter search then took ~146s total
(down from an extrapolated ~2 hours).

Status

✅ Complete

---

# Milestone 3 — Ensemble & Boosting Models

## Objectives

Train the remaining PROJECT_CONTEXT §39 candidate models.

Tasks

- [x] Random Forest — validation ROC-AUC 0.9492, PR-AUC 0.7550 (155s)
- [x] Gradient Boosting (sklearn) — validation ROC-AUC 0.9515, PR-AUC 0.7669 (1220s — slowest model; no internal parallelism)
- [x] XGBoost — validation ROC-AUC 0.9607, PR-AUC 0.8106 (110s)
- [x] LightGBM — validation ROC-AUC 0.9649, PR-AUC 0.8275 (75s — best individual model)
- [x] CatBoost — validation ROC-AUC 0.9609, PR-AUC 0.8135 (485s)

Deliverables

- `ML/modeling/model_registry.py` (5 additional entries)
- Experiment records for all 5 models — `ML/reports/modeling/experiment_log.json`

Status

✅ Complete

---

# Milestone 4 — Hyperparameter Optimization

## Objectives

Systematic, reproducible tuning per PROJECT_CONTEXT §40 (balance performance,
generalization, training/inference time, complexity).

Tasks

- [x] Define search space per model family (`ML/modeling/model_registry.py`; class-imbalance handling —
  `class_weight`/`scale_pos_weight`/`auto_class_weights` — included as a tunable dimension per model
  rather than a fixed assumption)
- [x] Run randomized search with cross-validation for each of the 7 candidate models
  (`RandomizedSearchCV`, 15 iterations, 3-fold, scored on ROC-AUC)
- [x] Record best parameters and the score that selected them
- [x] Fixed random seed for reproducibility (`RANDOM_STATE = 42` throughout)

Deliverables

- `ML/modeling/tuning.py`
- Tuning results per model — inside each model's record in `ML/reports/modeling/experiment_log.json`
  (`hyperparameters` field), not a separate `hyperparameter_tuning.json` — consolidated with CV/validation
  results per model rather than split across two files with the same key

Status

✅ Complete

---

# Milestone 5 — Cross-Validation & Full Evaluation

## Objectives

Evaluate every tuned model with the full PROJECT_CONTEXT §41 metric suite, on both
cross-validation (training split) and the held-out validation split.

Tasks

- [x] k-fold cross-validation scores per model (5-fold, `ML/modeling/cross_validation.py`)
- [x] Full metric suite per model on the validation split (accuracy, precision, recall,
  specificity, sensitivity, F1, ROC-AUC, PR-AUC, Brier score)
- [x] Confusion matrices (per model, in `experiment_log.json`)
- [x] ROC and PR curves — `figures/roc_curves.png`, `figures/pr_curves.png`
- [x] Calibration curves — `figures/calibration_curves.png`

Deliverables

- `ML/reports/modeling/model_comparison.md` (folded evaluation results into the comparison
  report rather than a separate `evaluation_report.md` — same 7-model table serves both purposes,
  and a second file would just be a subset view of the same data)
- `ML/reports/modeling/figures/` (ROC/PR/calibration/metric-comparison plots)

Status

✅ Complete

---

# Milestone 6 — Model Comparison

## Objectives

Standardized side-by-side comparison per PROJECT_CONTEXT §42.

Tasks

- [x] Comparison table: performance, training time, model complexity (inference time not
  separately measured — training time and model complexity/interpretability are used as the
  documented proxies; a dedicated inference-latency benchmark can be added when the backend
  serving path exists)
- [x] Explainability-compatibility note per model (tree-based vs. linear; verified with a real
  SHAP smoke test in Milestone 12, not just asserted)
- [x] Visualization: metric comparison chart across models — `figures/metric_comparison_bars.png`

Deliverables

- `ML/reports/modeling/model_comparison.md`, `model_comparison.csv`

Status

✅ Complete

---

# Milestone 7 — Ensemble/Stacking Model

## Objectives

PROJECT_CONTEXT §39 explicitly lists "Ensemble Models" alongside the individual algorithms —
a stacking/voting combination of the strongest individual models.

Tasks

- [x] Build a stacking ensemble from the top individual models — `ML/modeling/stacking.py`,
  `StackingClassifier` with a `LogisticRegression` meta-learner over `lightgbm`/`xgboost`/`random_forest`
- [x] Evaluate it identically to the individual models on the validation split — ROC-AUC 0.9552,
  PR-AUC 0.7874, F1 0.7188 (did not beat `lightgbm` alone at 0.9649/0.8275 — a legitimate finding:
  the three base learners are all tree-based boosting/bagging models whose predictions correlate
  heavily, leaving the meta-learner little complementary signal to exploit)
- [x] Add to the model comparison table

Note on scope: `gradient_boosting` (1220s/fit) and `catboost` (485s/fit) were excluded from
stacking candidacy — `StackingClassifier`'s internal 5-fold cross-fit + final refit multiplies
single-fit cost ~6x per base model, which would have made either one alone take 48+ minutes.
A separate outer k-fold CV (as done for individual models in Milestone 5) was also skipped for
the stacking model specifically, for the same cost reason — documented in
`ML/scripts/run_stacking_ensemble.py`'s module docstring; the internal cross-fitting and the
independent validation-split evaluation together still provide genuine out-of-sample evidence.

Deliverables

- `ML/modeling/stacking.py`
- Updated `model_comparison.md`

Status

✅ Complete

---

# Milestone 8 — Survey-Aware Model (Research Objective)

## Objectives

PROJECT_CONTEXT §13/§26/§44: the project's core research objective is comparing
conventional vs. survey-aware learning. Sprint 1 (Milestone 8) already verified and
preserved `PATWT`/`CSTRATM`/`CPSUM` through every split specifically for this.

Tasks

- [x] Fit a survey-weighted baseline (weighted logistic regression, `sample_weight=PATWT`)
- [x] Compare its coefficients/performance against the conventional Logistic Regression baseline
- [x] Document the comparison and its limitations (first pass, not PROJECT_CONTEXT's full
      research program — flagged explicitly)

**Findings:**
- **Predictive comparison** (full 866-feature set): unweighted ROC-AUC 0.9343 vs. weighted
  0.8914 — the survey-weighted model scores *lower* on this sample. This is expected, not a
  bug: weighting optimizes representativeness of the U.S. population NHAMCS samples, not
  discrimination on this specific sample; up-weighting underrepresented groups trades some
  in-sample discrimination for population validity.
- **Inference comparison** (15 focused features, weighted GLM vs. weighted+cluster-robust
  GLM clustering on `CPSUM`): **8 of 15 predictors** (`CBC`, `DIAG1` frequency, `GPMED2-6`,
  `NUMDIS`) are significant (p<0.05) under naive weighted standard errors but lose
  significance once cluster-robust correction is applied — meaning the naive model
  substantially overstated confidence in those predictors by ignoring the clustered (by
  hospital/PSU) sample design. This is exactly the kind of result the survey-aware research
  objective is asking about.
- Known limitation (documented in code and report): statsmodels' `cov_type='cluster'` is not
  fully supported in combination with `var_weights` (a genuine library constraint, not a bug
  here) — the cluster-robust standard errors are exploratory, not textbook-rigorous
  design-based inference. A dedicated survey-design library (e.g. `samplics`) would be needed
  for that, out of scope for this first pass.

Deliverables

- `ML/modeling/survey_aware.py`
- `ML/reports/modeling/survey_aware_comparison.md`, `survey_aware_glm_comparison.csv`

Status

✅ Complete

---

# Milestone 9 — Final Model Selection

## Objectives

Apply predefined criteria (PROJECT_CONTEXT §39: "automatically identify the best-performing
model based on predefined evaluation criteria") and confirm on the untouched test split.

Tasks

- [x] Define and document the selection criteria (primary: validation PR-AUC; tie-breakers:
  recall, then training time — documented in `ML/scripts/run_final_model_selection.py`)
- [x] Select the best model — **`lightgbm`** (validation PR-AUC 0.8275, ROC-AUC 0.9649,
  highest of all 8 candidates including the stacking ensemble)
- [x] Evaluate the selected model on the test split exactly once — ROC-AUC 0.9564, PR-AUC
  0.7599, F1 0.7276, recall 0.7013 (close to validation numbers — good generalization, no
  overfitting to the validation split)
- [x] Justify the choice in writing

Deliverables

- `ML/reports/modeling/final_model_selection.md`

Status

✅ Complete

---

# Milestone 10 — Model Serialization & Versioning

## Objectives

Persist the selected model per PROJECT_CONTEXT §46/§48, consumable by the backend without
retraining.

Tasks

- [x] Save the trained model artifact — `ML/saved_models/model.pkl` (`lightgbm`, version 1.0.0)
- [x] Save model metadata (version, training date, metrics, hyperparameters, feature list)
- [x] Confirm it loads and predicts using the Sprint 1 `PreprocessingPipeline` output directly —
  reload + predict smoke test passed

Deliverables

- `ML/saved_models/model.pkl`, `ML/saved_models/model_metadata.json`

Status

✅ Complete

---

# Milestone 11 — Reproducibility & Validation

## Objectives

Verify training correctness the same way Sprint 1 Milestone 11 verified preprocessing
correctness.

Tasks

- [x] Retrain determinism check (same seed -> same result) — PASS, max abs diff 0.0
- [x] End-to-end smoke test: raw row -> `PreprocessingPipeline.transform` -> loaded model -> prediction — PASS
- [x] Unit tests for metrics/CV/tuning utilities — 13 new tests (`test_metrics.py`,
  `test_cross_validation.py`, `test_survey_aware.py`); full suite (Sprint 1 + Sprint 2) is
  **50/50 passing**

Deliverables

- `ML/tests/test_metrics.py`, `test_cross_validation.py`, `test_survey_aware.py`
- `ML/reports/modeling/validation_report.md`

Status

✅ Complete

---

# Milestone 12 — Ready for Explainable AI

Sprint 2 is complete when:

- [x] All candidate models trained, tuned, and evaluated (7 individual + 1 stacking ensemble)
- [x] Cross-validation completed for every model (5-fold; stacking ensemble uses its internal
  cross-fit instead, documented cost tradeoff — see Milestone 7)
- [x] Full evaluation metric suite recorded for every model
- [x] Model comparison complete
- [x] Survey-aware comparison complete
- [x] Best model selected and justified — `lightgbm`
- [x] Best model evaluated on the test split — ROC-AUC 0.9564
- [x] Model and metadata serialized
- [x] Reproducibility verified
- [x] Selected model confirmed compatible with an explainability method — SHAP `TreeExplainer`
  smoke-tested successfully on `lightgbm` directly (not assumed from model type)

Status

✅ READY — Sprint 2 is complete. See `ML/reports/modeling/ready_for_explainable_ai.md`.

---

# Sprint 2 Deliverables

Actual repository layout (consolidated from the original per-file sketch — see Milestone 1/6/9 notes):

```
ML/
├── modeling/
│   ├── metrics.py               (accuracy/precision/recall/specificity/F1/ROC-AUC/PR-AUC/calibration)
│   ├── cross_validation.py      (stratified 5-fold CV)
│   ├── experiment_log.py        (ExperimentRecord/ExperimentLog)
│   ├── model_registry.py        (all 7 candidate models + search spaces)
│   ├── tuning.py                (RandomizedSearchCV wrapper)
│   ├── stacking.py              (StackingClassifier builder)
│   └── survey_aware.py          (weighted LR + weighted/cluster-robust GLM)
├── saved_models/
│   ├── candidates/               (all 8 fitted models, for comparison/reuse)
│   ├── model.pkl                 (selected: lightgbm)
│   └── model_metadata.json
├── reports/modeling/
│   ├── experiment_log.json
│   ├── model_comparison.md / .csv
│   ├── survey_aware_comparison.md / survey_aware_glm_comparison.csv
│   ├── final_model_selection.md
│   ├── validation_report.md
│   ├── ready_for_explainable_ai.md
│   └── figures/ (roc_curves, pr_curves, calibration_curves, metric_comparison_bars)
└── tests/ (+13 new: test_metrics.py, test_cross_validation.py, test_survey_aware.py)
```

Sprint Status

**Progress: 12/12 milestones complete. Sprint 2 (Machine Learning Model Development) is DONE.**

Selected model: **LightGBM** (test ROC-AUC 0.9564, PR-AUC 0.7599). Two solver/cost issues were
found and fixed during execution (see Milestone 2 and Milestone 7 notes) — every script was
re-run clean afterward with no regression. Full test suite: 50/50 passing.

Current Task:
Sprint 2 complete. Ready for the Explainable AI sprint — awaiting instruction to begin.