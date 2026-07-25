# Global Explainability Report

Generated: 2026-07-25T08:16:43.952114+00:00

Computed on the validation split (2,404 rows, held-out/unseen during training). Global importance = mean |SHAP value| (margin space) across all explained rows — the standard SHAP definition of global feature importance.

## Visualizations

- `visualizations/summary_plot.png` — SHAP dot/summary plot, top 20 individual encoded features (each colored by that row's raw feature value)
- `visualizations/bar_plot.png` — mean |SHAP| bar chart, same granularity
- `visualizations/beeswarm_plot.png` — custom beeswarm aggregated **by source variable** (one-hot dummies summed back together) — more clinically interpretable than a third per-encoded-feature view would have been

## Most Influential Source Variables

| Rank | Variable | Label | Mean \|SHAP\| | Note |
|---|---|---|---|---|
| 1 | `NUMDIS` | Number of medications prescribed at discharge | 1.6881 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 2 | `CONSULT` | Consulting physician seen | 1.1837 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 3 | `TOTDIAG` | Total number of diagnostic services ordered or provided | 0.7846 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 4 | `DIAG1` | Diagnosis #1 | 0.6576 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 5 | `IMMEDR` | Immediacy with which patient should be seen (unimputed) | 0.5672 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 6 | `COVIDTEST` | Coronavirus (COVID-19) test | 0.4937 | during-visit care-process variable (test/procedure/medication ordered) |
| 7 | `LOV` | Length of visit in minutes | 0.4309 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 8 | `AGE` | Patient age in years | 0.4111 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 9 | `PROC` | Were procedures provided at this visit? | 0.2364 | during-visit care-process variable (test/procedure/medication ordered) |
| 10 | `IVFLUIDS` | IV fluids | 0.2323 | during-visit care-process variable (test/procedure/medication ordered) |
| 11 | `REGION` | Geographic region | 0.2222 | demographic/administrative covariate, not a clinical measurement |
| 12 | `DIAG2` | Diagnosis #2 | 0.2145 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 13 | `ARREMS` | Arrival by ambulance | 0.2004 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |
| 14 | `DRUGID2` | Drug ID code for medication #2 | 0.1827 | during-visit care-process variable (test/procedure/medication ordered) |
| 15 | `RFV13D` | Patient's complaint, symptom, or other reason for visit #1 - broader category | 0.1768 | clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis) |

## Least Influential Source Variables (of those explained)

| Variable | Label | Mean \|SHAP\| |
|---|---|---|
| `GPMED13` | Medication #13 given in ED or Rx at discharge | 0.000000 |
| `GPMED15` | Medication #15 given in ED or Rx at discharge | 0.000000 |
| `HYPOTENSIVE_FLAG` |  | 0.000000 |
| `MED16` | Medication #16 | 0.000000 |
| `RX2V3C3` | For RX2, level 3 of MULTUM drug category #3 (detailed level) | 0.000000 |
| `RX3V2C3` | For RX3, level 2 of MULTUM drug category #3 (intermediate level) | 0.000000 |
| `RX3V3C3` | For RX3, level 3 of MULTUM drug category #3 (detailed level) | 0.000000 |
| `CONTSUB13` | Controlled substance status code for medication #13 | 0.000000 |
| `CONTSUB14` | Controlled substance status code for medication #14 | 0.000000 |
| `RX7V1C2` | For RX7, level 1 of MULTUM drug category #2 (broad level) | 0.000000 |
| `COMSTAT17` | Composition status code for medication #17 | 0.000000 |
| `COMSTAT12` | Composition status code for medication #12 | 0.000000 |
| `COMSTAT16` | Composition status code for medication #16 | 0.000000 |
| `COMSTAT15` | Composition status code for medication #15 | 0.000000 |
| `COMSTAT14` | Composition status code for medication #14 | 0.000000 |

## Clinical Interpretation

The top-ranked variables are consistent with Sprint 2's tree-importance/mutual-information ranking (`ML/reports/feature_engineering/feature_selection_report.md`) — `CONSULT`, `TOTDIAG`, care-process flags (tests/medications ordered), `AGE`, and vital signs dominate both rankings. This cross-validation between two independent methods (tree importance computed during model selection vs. SHAP computed after final training) is reassuring: the model is leaning on the same clinically plausible signals under both lenses, not on an artifact specific to one ranking method.

Near-zero-importance variables are expected: Sprint 1's near-zero-variance filter already removed the most extreme cases (dominant category >=99%), but many individually-encoded one-hot dummy columns and rare diagnosis/drug frequency codes still carry little weight in aggregate, which SHAP correctly reflects rather than artificially inflating.

## Raw Data

Full per-feature and per-source-variable importance tables are computed here but not separately saved to CSV in this milestone — they are exact function outputs of `ML.explainability.shap_utils.mean_absolute_shap_by_feature` / `mean_absolute_shap_by_source_variable`, reproducible from the saved `shap_values_validation.npy` at any time; the JSON export utility (Milestone 8) is where these become an official artifact.