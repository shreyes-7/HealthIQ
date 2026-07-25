# Survey-Weighted vs. Unweighted LightGBM

Generated: 2026-07-25T10:52:04.941653+00:00

Same LightGBM hyperparameters (from `experiment_log.json`, the exact production tuning result), same training data, same `class_weight="balanced"` setting -- the **only** difference is `sample_weight=PATWT` on the weighted variant. This isolates the effect of survey weighting specifically, the same experimental design Sprint 2 used for its Logistic Regression comparison, now applied to the actual production model for the first time.

## Validation Split

| Metric | Unweighted (production) | Weighted (survey-aware) | Difference |
|---|---|---|---|
| accuracy | 0.9330 | 0.9326 | -0.0004 |
| precision | 0.7716 | 0.7617 | -0.0099 |
| recall | 0.7013 | 0.7138 | +0.0126 |
| specificity | 0.9684 | 0.9660 | -0.0024 |
| f1 | 0.7348 | 0.7370 | +0.0023 |
| roc_auc | 0.9649 | 0.9627 | -0.0022 |
| pr_auc | 0.8275 | 0.8148 | -0.0127 |
| brier_score | 0.0528 | 0.0555 | +0.0027 |

## Test Split

| Metric | Unweighted (production) | Weighted (survey-aware) | Difference |
|---|---|---|---|
| accuracy | 0.9305 | 0.9268 | -0.0037 |
| precision | 0.7559 | 0.7351 | -0.0208 |
| recall | 0.7013 | 0.6981 | -0.0031 |
| specificity | 0.9655 | 0.9616 | -0.0038 |
| f1 | 0.7276 | 0.7161 | -0.0114 |
| roc_auc | 0.9564 | 0.9534 | -0.0030 |
| pr_auc | 0.7599 | 0.7408 | -0.0191 |
| brier_score | 0.0593 | 0.0626 | +0.0033 |

## Interpretation

As in Sprint 2's Logistic Regression comparison, expect the weighted model's raw discrimination metrics on this sample to be lower, not higher -- `PATWT` up-weights visits from underrepresented sampling strata to better reflect the U.S. population NHAMCS samples, which trades some in-sample predictive accuracy for population representativeness. That is the expected, correct behavior of a survey-weighted estimator, not a sign the weighted model is worse in an absolute sense -- see the fairness audit (`fairness_audit_report.md`) for whether that trade produces a more equitable model across demographic groups, which is the more relevant question for this project's research objective than raw accuracy alone.