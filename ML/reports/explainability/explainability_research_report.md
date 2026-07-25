# Explainability Research Report

Generated: 2026-07-25T10:03:38.655436+00:00

Emergency Department Admission Prediction — SHAP-Based Explainability Analysis

Model: `lightgbm` (version 1.0.0), 866 features. Explanations computed on the validation split (2,404 held-out visits, unseen during training).

---

## 1. Feature Importance Table

Top 20 source variables by mean |SHAP value| (margin/log-odds space), aggregated across each variable's one-hot encoded columns.

| Rank | Variable | Label | Mean \|SHAP\| |
|---|---|---|---|
| 1 | `NUMDIS` | Number of medications prescribed at discharge | 1.6881 |
| 2 | `CONSULT` | Consulting physician seen | 1.1837 |
| 3 | `TOTDIAG` | Total number of diagnostic services ordered or provided | 0.7846 |
| 4 | `DIAG1` | Diagnosis #1 | 0.6576 |
| 5 | `IMMEDR` | Immediacy with which patient should be seen (unimputed) | 0.5672 |
| 6 | `COVIDTEST` | Coronavirus (COVID-19) test | 0.4937 |
| 7 | `LOV` | Length of visit in minutes | 0.4309 |
| 8 | `AGE` | Patient age in years | 0.4111 |
| 9 | `PROC` | Were procedures provided at this visit? | 0.2364 |
| 10 | `IVFLUIDS` | IV fluids | 0.2323 |
| 11 | `REGION` | Geographic region | 0.2222 |
| 12 | `DIAG2` | Diagnosis #2 | 0.2145 |
| 13 | `ARREMS` | Arrival by ambulance | 0.2004 |
| 14 | `DRUGID2` | Drug ID code for medication #2 | 0.1827 |
| 15 | `RFV13D` | Patient's complaint, symptom, or other reason for visit #1 - broader category | 0.1768 |
| 16 | `EDPRIM` | When patients with identified primary care physicians (PCP) arrive at the ED, how often do you electronically send notifications to the patients' PCP? | 0.1717 |
| 17 | `VMONTH` | Month of Visit | 0.1704 |
| 18 | `BLOODCX` | Blood culture | 0.1703 |
| 19 | `SURGDAY` | How many days in a week are inpatient elective surgeries scheduled? | 0.1604 |
| 20 | `MED2` | Medication #2 | 0.1520 |

## 2. Global Interpretation

The five most influential variables — `NUMDIS` (medications prescribed at discharge), `CONSULT` (consulting physician seen), `TOTDIAG` (diagnostic services ordered), `DIAG1` (primary diagnosis), and `IMMEDR` (triage acuity) — are all **during-visit care-process or clinical-severity indicators**, not administrative artifacts. This was independently corroborated by Sprint 2's tree-importance/mutual-information feature selection ranking (`ML/reports/feature_engineering/feature_selection_report.md`), computed by a completely different method before final model training. Two independent measurements agreeing on which signals matter is meaningfully more reassuring than either alone.

Dependence analysis (Milestone 5) found `AGE`'s relationship to admission risk is **nonlinear**: flat-to-slightly-negative contribution through younger and middle-aged patients, then a clear upward inflection for older patients — consistent with established clinical knowledge that elderly ED patients are admitted at substantially higher rates.

## 3. Local Interpretation

Three cases were explained in depth (Milestone 4), selected programmatically rather than hand-picked: a confident correctly-predicted admission (P=0.9999), a confident correctly-predicted discharge (P=0.0000), and the model's single most uncertain prediction in the validation split (P=0.5067). The borderline case is the most instructive: `CONSULT`, `NUMDIS`, and `TOTDIAG` pushed toward admission while a low-frequency diagnosis code and younger age pulled the other way, landing the prediction almost exactly on the decision boundary — a legible, clinically sensible story rather than an opaque number. Full detail: `ML/reports/explainability/patient_explanations/`.

## 4. Clinical Findings

- Mean predicted P(admit) is 0.694 among actually-admitted validation patients vs. 0.035 among actually-discharged patients — the model's predicted risk separates the two groups by a wide margin, consistent with its 0.9564 test-split ROC-AUC (Sprint 2).
- The `older_adult_65_plus` cohort has the highest mean predicted admission probability (0.277) of any age group, and is the *only* age group where `AGE` itself enters the top-5 locally-important features — the model leans on age specifically, and only, within the population where it is most clinically relevant.
- Ambulance-arrival patients (`arrival_mode=1`) show roughly 3x the mean predicted admission probability (0.279) of other arrival modes (0.085) — consistent with ambulance transport correlating with acuity.
- Across every cohort dimension examined (admission status, age group, gender, arrival mode, triage level), the same 2-3 features top the ranking — the model applies a consistent decision process across subgroups rather than a fundamentally different one per group, which is a desirable property for a clinical decision-support tool.

## 5. Limitations

- **SHAP explains the model, not medical reality.** A feature ranking highly means the model relies on it, not that it is the true causal driver of admission — the usual correlation-vs-causation caveat applies, sharpened by the fact this is an ML model trained on observational EHR-survey data, not a randomized study.
- **One-hot encoding fragments variable importance.** Every ranking in this report uses source-variable aggregation (summing a variable's one-hot dummy columns' SHAP contributions) specifically to correct for this — the raw per-encoded-feature ranking alone would understate variables with many categories.
- **Explanation Validation (Milestone 7) checked mathematical consistency and the preprocessing handoff, not clinical correctness or fairness.** No formal bias/fairness audit across protected attributes (e.g. race, ethnicity, insurance type) has been performed; the cohort analysis (Milestone 6) checked *consistency* of reasoning across subgroups, which is a related but distinct question from fairness in outcomes.
- **Per-request explanation latency (~1.2s) is borderline for a truly interactive API** (Milestone 8) — dominated by the cleaning pipeline's per-row overhead, not SHAP itself.
- **Dependence plots use `feature_perturbation="tree_path_dependent"`** (SHAP's default for `TreeExplainer`), which can attribute some credit to correlated features jointly rather than cleanly isolating one from another — relevant for reading the `BPSYS`/`BPDIAS` or `PULSE`/`PULSED` dependence plots, since Sprint 1 EDA found these pairs correlated at 0.77-0.98.

## 6. Future Work

- SHAP interaction values (`shap.TreeExplainer.shap_interaction_values`) for a rigorous, pairwise interaction analysis, rather than the single-interaction-feature coloring used in Milestone 5's dependence plots.
- A formal fairness/bias audit across demographic cohorts (race, ethnicity, payer type), extending Milestone 6's consistency check into an outcome-equity analysis.
- Backend integration (Sprint 4): `ML/explainability/service.py` is ready to be wrapped by a FastAPI endpoint; the ~1.2s per-request latency noted in Milestone 8 is worth profiling before that integration if sub-200ms responses are required.
- Explanation drift monitoring: re-run Milestone 7's validation checks periodically once the model is serving live traffic, to catch preprocessing/model drift early.
- Extend the survey-aware comparison (Sprint 2 Milestone 8) into the explainability layer: do SHAP-based explanations differ meaningfully between a weighted and unweighted model?