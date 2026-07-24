# Final Model Selection Report

Generated: 2026-07-24T19:42:12.024511+00:00

## Selection Criteria

1. Primary: validation PR-AUC (more informative than ROC-AUC at ~13% positive rate)
2. Tie-breaker: recall/sensitivity (under-predicting admission risk is the costlier clinical error)
3. Tie-breaker: training time, then interpretability

## Selected Model: `lightgbm`

### Validation metrics (informed the selection)

| model    | interpretability   |   accuracy |   precision |   recall |   specificity |     f1 |   roc_auc |   pr_auc |   brier_score |   cv_roc_auc_mean |   cv_roc_auc_std |   training_time_seconds |
|:---------|:-------------------|-----------:|------------:|---------:|--------------:|-------:|----------:|---------:|--------------:|------------------:|-----------------:|------------------------:|
| lightgbm | medium             |      0.933 |      0.7716 |   0.7013 |        0.9684 | 0.7348 |    0.9649 |   0.8275 |        0.0528 |            0.9518 |           0.0071 |                  74.922 |

### Test split metrics (confirmation only -- evaluated exactly once)

|   accuracy |   precision |   recall |   sensitivity |   specificity |     f1 |   roc_auc |   pr_auc |   brier_score |   threshold |
|-----------:|------------:|---------:|--------------:|--------------:|-------:|----------:|---------:|--------------:|------------:|
|     0.9305 |      0.7559 |   0.7013 |        0.7013 |        0.9655 | 0.7276 |    0.9564 |   0.7599 |        0.0593 |         0.5 |

Confusion matrix (test): {'true_negative': 2014, 'false_positive': 72, 'false_negative': 95, 'true_positive': 223}
