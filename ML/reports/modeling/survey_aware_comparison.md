# Survey-Aware Model Comparison Report

Generated: 2026-07-24T19:41:04.003157+00:00

**Scope**: a first pass, not the full research program PROJECT_CONTEXT.md Section 44 envisions. Two comparisons are made — see `ML/modeling/survey_aware.py` docstring for the reasoning behind each.

## 1. Predictive Comparison (full 866-feature set)

Same `LogisticRegression`, same features, same validation split — only difference is `sample_weight=PATWT` on the weighted version.

| Metric | Unweighted (conventional) | Weighted (survey-aware) |
|---|---|---|
| accuracy | 0.9156 | 0.9106 |
| precision | 0.7255 | 0.6988 |
| recall | 0.5818 | 0.5692 |
| f1 | 0.6457 | 0.6274 |
| roc_auc | 0.9343 | 0.8914 |
| pr_auc | 0.7257 | 0.6472 |
| brier_score | 0.0616 | 0.0705 |

## 2. Inference Comparison (focused feature subset)

Features used (15, Sprint 1's top-ranked by combined importance): ['TOTDIAG', 'CONSULT__Yes', 'NUMDIS', 'NUMGIV', 'CBC__Yes', 'LOV', 'IVFLUIDS__Yes', 'DIAG1__frequency', 'AGE', 'GPMED6__1', 'BLOODCX__Yes', 'GPMED2__1', 'GPMED4__1', 'GPMED3__1', 'GPMED5__1']

Weighted GLM (survey weight only, `var_weights=PATWT`) vs. the same GLM with cluster-robust standard errors (clustering on `CPSUM`, the PSU variable) — isolates what accounting for the clustered sample design changes, beyond weighting alone.

**Known limitation**: statsmodels emits `SpecificationWarning: cov_type not fully supported with var_weights` for the cluster-robust fit (a genuine statsmodels constraint, present regardless of weight type). The cluster-robust standard errors below should be read as exploratory, not textbook-rigorous design-based inference — a dedicated survey-design library would be needed for that, out of scope for this first pass.

|                  |   coefficient |   weighted_std_error |   weighted_p_value | significant_unweighted   |   cluster_robust_std_error |   cluster_robust_p_value | significant_cluster_robust   |
|:-----------------|--------------:|---------------------:|-------------------:|:-------------------------|---------------------------:|-------------------------:|:-----------------------------|
| const            |       -3.8028 |               0.0011 |                  0 | True                     |                     0.2924 |                   0      | True                         |
| TOTDIAG          |        0.2939 |               0.0005 |                  0 | True                     |                     0.1415 |                   0.0378 | True                         |
| CONSULT__Yes     |        1.817  |               0.0008 |                  0 | True                     |                     0.2316 |                   0      | True                         |
| NUMDIS           |       -0.241  |               0.0005 |                  0 | True                     |                     0.1966 |                   0.2202 | False                        |
| NUMGIV           |        0.29   |               0.0006 |                  0 | True                     |                     0.1085 |                   0.0075 | True                         |
| CBC__Yes         |        0.4456 |               0.0013 |                  0 | True                     |                     0.3006 |                   0.1382 | False                        |
| LOV              |        0.1708 |               0.0003 |                  0 | True                     |                     0.0763 |                   0.0252 | True                         |
| IVFLUIDS__Yes    |        0.5185 |               0.0009 |                  0 | True                     |                     0.1655 |                   0.0017 | True                         |
| DIAG1__frequency |      -16.1264 |               0.051  |                  0 | True                     |                     8.4715 |                   0.057  | False                        |
| AGE              |        0.5537 |               0.0004 |                  0 | True                     |                     0.084  |                   0      | True                         |
| GPMED6__1        |        0.1182 |               0.0017 |                  0 | True                     |                     0.2057 |                   0.5655 | False                        |
| BLOODCX__Yes     |        0.8634 |               0.0012 |                  0 | True                     |                     0.1997 |                   0      | True                         |
| GPMED2__1        |        0.3401 |               0.0011 |                  0 | True                     |                     0.1743 |                   0.0511 | False                        |
| GPMED4__1        |       -0.1414 |               0.0014 |                  0 | True                     |                     0.188  |                   0.4521 | False                        |
| GPMED3__1        |        0.2174 |               0.0013 |                  0 | True                     |                     0.1272 |                   0.0875 | False                        |
| GPMED5__1        |        0.0633 |               0.0016 |                  0 | True                     |                     0.2056 |                   0.7583 | False                        |

- Significant (p < 0.05) under weighting alone but NOT after cluster correction: ['CBC__Yes', 'DIAG1__frequency', 'GPMED2__1', 'GPMED3__1', 'GPMED4__1', 'GPMED5__1', 'GPMED6__1', 'NUMDIS']
- Significant only after cluster correction: none

If either list above is non-empty, it means the naive (non-cluster-robust) model would have over- or under-stated confidence in that predictor — exactly the kind of finding PROJECT_CONTEXT.md's survey-aware research objective is asking about.
