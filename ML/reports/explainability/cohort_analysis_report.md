# Cohort Explainability Report

Generated: 2026-07-25T08:27:22.786759+00:00

Compares SHAP-based feature importance and mean predicted probability across patient subgroups. Cohort categories were reconstructed from their one-hot encoded columns using the encoder's own saved reference-category metadata, not hand-listed.

## Admission Vs Discharge

| Group | N | Mean P(admit) | Top 5 Features by Mean \|SHAP\| |
|---|---|---|---|
| admitted | 318 | 0.6936 | CONSULT, NUMDIS, TOTDIAG, COVIDTEST, DIAG1 |
| not_admitted | 2086 | 0.0355 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |

Distribution plot: `cohort_plots/admission_vs_discharge_shap_distribution.png`

## Age Group

| Group | N | Mean P(admit) | Top 5 Features by Mean \|SHAP\| |
|---|---|---|---|
| adolescent_13_17 | 107 | 0.0256 | NUMDIS, CONSULT, TOTDIAG, IMMEDR, DIAG1 |
| adult_18_64 | 1428 | 0.1025 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |
| child_2_12 | 265 | 0.0403 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |
| infant_0_1 | 124 | 0.0149 | NUMDIS, DIAG1, CONSULT, TOTDIAG, IMMEDR |
| older_adult_65_plus | 480 | 0.2769 | NUMDIS, CONSULT, TOTDIAG, AGE, DIAG1 |

Distribution plot: `cohort_plots/age_group_shap_distribution.png`

## Gender

| Group | N | Mean P(admit) | Top 5 Features by Mean \|SHAP\| |
|---|---|---|---|
| 1 | 1273 | 0.1187 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |
| 2 | 1131 | 0.1268 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |

Distribution plot: `cohort_plots/gender_shap_distribution.png`

## Arrival Mode

| Group | N | Mean P(admit) | Top 5 Features by Mean \|SHAP\| |
|---|---|---|---|
| 1 | 434 | 0.2786 | NUMDIS, CONSULT, TOTDIAG, DIAG1, AGE |
| 2 | 1901 | 0.0853 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |
| Missing | 69 | 0.1668 | NUMDIS, CONSULT, ARREMS, TOTDIAG, DIAG1 |

Distribution plot: `cohort_plots/arrival_mode_shap_distribution.png`

## Triage Level

| Group | N | Mean P(admit) | Top 5 Features by Mean \|SHAP\| |
|---|---|---|---|
| 0 | 91 | 0.0674 | NUMDIS, CONSULT, DIAG1, TOTDIAG, COVIDTEST |
| 1 | 24 | 0.3629 | CONSULT, NUMDIS, TOTDIAG, AGE, DIAG1 |
| 2 | 253 | 0.3334 | NUMDIS, CONSULT, TOTDIAG, IMMEDR, DIAG1 |
| 3 | 788 | 0.1354 | NUMDIS, CONSULT, TOTDIAG, DIAG1, COVIDTEST |
| 4 | 416 | 0.0115 | NUMDIS, CONSULT, IMMEDR, TOTDIAG, DIAG1 |
| 5 | 50 | 0.0001 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |
| 7 | 164 | 0.0720 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |
| Missing | 618 | 0.1166 | NUMDIS, CONSULT, TOTDIAG, DIAG1, IMMEDR |

Distribution plot: `cohort_plots/triage_level_shap_distribution.png`

## Interpretation

Where the same 2-3 features top the ranking across every group within a dimension, the model is applying a consistent decision process rather than a different one per subgroup. Where the ranking or mean predicted probability differs substantially between groups, that reflects genuine differences in the underlying population risk (e.g. older-age cohorts having a higher base admission rate) rather than necessarily indicating a problem — see the age-group and admission-vs-discharge tables above, and the `AGE` dependence plot from Milestone 5 for the same signal from a different angle.