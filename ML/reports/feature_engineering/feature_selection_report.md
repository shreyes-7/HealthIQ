# Feature Selection Report

Generated: 2026-07-24T17:43:03.950469+00:00

Computed on the training split only (train.parquet) — mutual information and tree-based importance never see validation or test data, so the selection ranking itself cannot leak held-out information.

**No model was trained or evaluated.** The RandomForest used to compute tree importance is a lightweight, unsaved, unscored ranking utility (see `ML/feature_engineering/feature_selection.py` docstring) — a different thing from the properly trained and validated predictive model Phase 2 will build.

## Method

- **Mutual Information** (`sklearn.feature_selection.mutual_info_classif`): target-aware, model-free, captures non-linear relationships.
- **Tree-based Importance** (`RandomForestClassifier`, 200 trees, max_depth=12): captures interactions the univariate mutual-information score misses.
- **Recursive Feature Elimination: skipped.** With 800+ encoded features, RFE requires refitting an estimator once per elimination step — computationally excessive for a selection utility and largely redundant with the importance ranking above.
- **Clinical relevance review**: automated only to the extent of cross-referencing top-ranked source variables against their NHAMCS codebook label (`ML/reports/data_dictionary.csv`); a genuine clinical-expert review is not an automatable step and remains open.

## Top 25 Features by Combined Rank (encoded, individual)

| Rank | Feature | Source Variable | Mutual Info | Tree Importance |
|---|---|---|---|---|
| 1 | `TOTDIAG` | `TOTDIAG` | 0.0836 | 0.0370 |
| 2 | `CONSULT__Yes` | `CONSULT` | 0.0626 | 0.0444 |
| 3 | `NUMDIS` | `NUMDIS` | 0.0450 | 0.0235 |
| 4 | `NUMGIV` | `NUMGIV` | 0.0562 | 0.0151 |
| 5 | `CBC__Yes` | `CBC` | 0.0483 | 0.0121 |
| 6 | `LOV` | `LOV` | 0.0387 | 0.0199 |
| 7 | `IVFLUIDS__Yes` | `IVFLUIDS` | 0.0442 | 0.0132 |
| 8 | `DIAG1__frequency` | `DIAG1` | 0.0396 | 0.0108 |
| 9 | `AGE` | `AGE` | 0.0316 | 0.0183 |
| 10 | `GPMED6__1` | `GPMED6` | 0.0325 | 0.0118 |
| 11 | `BLOODCX__Yes` | `BLOODCX` | 0.0326 | 0.0115 |
| 12 | `GPMED2__1` | `GPMED2` | 0.0359 | 0.0083 |
| 13 | `GPMED4__1` | `GPMED4` | 0.0346 | 0.0082 |
| 14 | `GPMED3__1` | `GPMED3` | 0.0338 | 0.0085 |
| 15 | `GPMED5__1` | `GPMED5` | 0.0324 | 0.0096 |
| 16 | `RFV13D__frequency` | `RFV13D` | 0.0342 | 0.0063 |
| 17 | `DRUGID1__frequency` | `DRUGID1` | 0.0384 | 0.0055 |
| 18 | `RX2CAT1__frequency` | `RX2CAT1` | 0.0350 | 0.0057 |
| 19 | `EKG__Yes` | `EKG` | 0.0300 | 0.0098 |
| 20 | `COVIDTEST__Yes` | `COVIDTEST` | 0.0287 | 0.0114 |
| 21 | `RX1CAT1__frequency` | `RX1CAT1` | 0.0424 | 0.0051 |
| 22 | `MED1__frequency` | `MED1` | 0.0376 | 0.0051 |
| 23 | `DRUGID2__frequency` | `DRUGID2` | 0.0370 | 0.0051 |
| 24 | `CMP__Yes` | `CMP` | 0.0306 | 0.0059 |
| 25 | `DRUGID3__frequency` | `DRUGID3` | 0.0340 | 0.0050 |

## Top 25 Source Variables (aggregated across their encoded columns)

This view is more clinically interpretable: one-hot encoding splits a single source variable (e.g. `AGE_GROUP`) across several dummy columns, diluting its individual-column rank above. Aggregating recovers each variable's total contribution.

| Rank | Variable | Label (from data dictionary) | Mutual Info (sum) | Tree Importance (sum) |
|---|---|---|---|---|
| 1 | `CONSULT` | Consulting physician seen | 0.0626 | 0.0444 |
| 2 | `TOTDIAG` | Total number of diagnostic services ordered or provided | 0.0836 | 0.0370 |
| 3 | `NUMDIS` | Number of medications prescribed at discharge | 0.0450 | 0.0235 |
| 4 | `LOV` | Length of visit in minutes | 0.0387 | 0.0199 |
| 5 | `AGE` | Patient age in years | 0.0316 | 0.0183 |
| 6 | `NUMGIV` | Number of medications given in ED | 0.0562 | 0.0151 |
| 7 | `GPMED6` | Medication #6 given in ED or Rx at discharge | 0.0325 | 0.0134 |
| 8 | `IVFLUIDS` | IV fluids | 0.0442 | 0.0132 |
| 9 | `CBC` | CBC (Complete blood count) | 0.0483 | 0.0121 |
| 10 | `PTTINR` | Prothrombin time (PT/PTT/INR) | 0.0228 | 0.0115 |
| 11 | `BLOODCX` | Blood culture | 0.0326 | 0.0115 |
| 12 | `COVIDTEST` | Coronavirus (COVID-19) test | 0.0287 | 0.0114 |
| 13 | `DIAG1` | Diagnosis #1 | 0.0396 | 0.0108 |
| 14 | `GPMED5` | Medication #5 given in ED or Rx at discharge | 0.0331 | 0.0107 |
| 15 | `GPMED2` | Medication #2 given in ED or Rx at discharge | 0.0517 | 0.0100 |
| 16 | `EKG` | EKG/ECG | 0.0300 | 0.0098 |
| 17 | `GPMED3` | Medication #3 given in ED or Rx at discharge | 0.0441 | 0.0097 |
| 18 | `AGE_GROUP` |  | 0.0332 | 0.0094 |
| 19 | `GPMED4` | Medication #4 given in ED or Rx at discharge | 0.0396 | 0.0094 |
| 20 | `TOTCHRON` | Total number of chronic conditions | 0.0305 | 0.0092 |
| 21 | `BPDIAS` | Initial vital signs: Blood pressure - Diastolic | 0.0000 | 0.0088 |
| 22 | `SHOCK_INDEX` |  | 0.0027 | 0.0086 |
| 23 | `IMMEDR` | Immediacy with which patient should be seen (unimputed) | 0.0336 | 0.0084 |
| 24 | `ARREMS` | Arrival by ambulance | 0.0228 | 0.0081 |
| 25 | `VMONTH` | Month of Visit | 0.0177 | 0.0077 |

## Clinical Relevance Commentary

The top-ranked source variables were cross-checked against well-established emergency medicine admission risk factors (age, triage acuity, vital-sign abnormality, comorbidity burden, diagnosis, and care intensity during the visit) rather than an exhaustive literature review. One finding is worth calling out explicitly: `CONSULT` ranked #1 and was manually re-verified against the codebook before accepting it, since a "consulting physician" sounded like it could be disposition-adjacent leakage similar to the already-excluded `ADMTPHYS` (admitting physician). It is not: `CONSULT` is part of the codebook's "PROVIDERS SEEN" item block (item 219, alongside `ATTPHYS`/`RESINT`/`RNLPN`/etc.) — a during-visit care-process flag recording who saw the patient, structurally distinct from the post-admission `ADMTPHYS`. Diagnostic/procedure flags (`CBC`, `EKG`, `IVFLUIDS`, `BLOODCX`, `COVIDTEST`, `PTTINR`, `TOTDIAG`) are similarly legitimate: tests ordered during the visit inform the disposition decision rather than resulting from it, the same reasoning already applied to `TOTDIAG` in Milestone 5.

- `CONSULT`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `TOTDIAG`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `NUMDIS`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `LOV`: plausible but not in a recognized clinical category above — worth a manual look
- `AGE`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `NUMGIV`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `GPMED6`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `IVFLUIDS`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `CBC`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `PTTINR`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `BLOODCX`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `COVIDTEST`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `DIAG1`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `GPMED5`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `GPMED2`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `EKG`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `GPMED3`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `AGE_GROUP`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `GPMED4`: during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision
- `TOTCHRON`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `BPDIAS`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `SHOCK_INDEX`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `IMMEDR`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `ARREMS`: clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)
- `VMONTH`: plausible but not in a recognized clinical category above — worth a manual look

## Full Rankings

- Per-encoded-feature: `ML/reports/feature_engineering/feature_importance_scores.csv`
- Per-source-variable: `ML/reports/feature_engineering/source_variable_importance.csv`

## Recommendation

A ranked list, not a hard cutoff, is provided deliberately: the right feature count depends on the model family Phase 2 chooses (tree ensembles tolerate many weak features better than Logistic Regression does). `combined_rank` in the CSV gives a reasonable starting point for a top-K selection if one is needed.
