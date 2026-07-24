# Model Comparison Report

Standardized comparison across every candidate model, all evaluated identically on the same validation split with the same metric suite (PROJECT_CONTEXT.md Section 42).

| model               | interpretability    |   accuracy |   precision |   recall |   specificity |     f1 |   roc_auc |   pr_auc |   brier_score |   cv_roc_auc_mean |   cv_roc_auc_std |   training_time_seconds |
|:--------------------|:--------------------|-----------:|------------:|---------:|--------------:|-------:|----------:|---------:|--------------:|------------------:|-----------------:|------------------------:|
| lightgbm            | medium              |     0.933  |      0.7716 |   0.7013 |        0.9684 | 0.7348 |    0.9649 |   0.8275 |        0.0528 |            0.9518 |           0.0071 |                  74.922 |
| catboost            | medium              |     0.9089 |      0.6098 |   0.8648 |        0.9156 | 0.7152 |    0.9609 |   0.8135 |        0.0668 |            0.9453 |           0.0074 |                 485.312 |
| xgboost             | medium              |     0.9305 |      0.7871 |   0.6509 |        0.9732 | 0.7126 |    0.9607 |   0.8106 |        0.0516 |            0.9501 |           0.0076 |                 109.625 |
| stacking_ensemble   | low (meta-ensemble) |     0.9326 |      0.8023 |   0.6509 |        0.9756 | 0.7188 |    0.9552 |   0.7874 |        0.0529 |          nan      |         nan      |                 109.437 |
| gradient_boosting   | medium              |     0.9255 |      0.7565 |   0.6447 |        0.9684 | 0.6961 |    0.9515 |   0.7669 |        0.0557 |            0.9412 |           0.0076 |                1219.84  |
| random_forest       | medium              |     0.9222 |      0.7835 |   0.5692 |        0.976  | 0.6594 |    0.9492 |   0.755  |        0.0581 |            0.9383 |           0.0056 |                 155.109 |
| logistic_regression | high                |     0.8669 |      0.4982 |   0.8585 |        0.8682 | 0.6305 |    0.9387 |   0.7187 |        0.0984 |            0.9243 |           0.0077 |                 146.078 |
| decision_tree       | high                |     0.8303 |      0.4269 |   0.827  |        0.8308 | 0.5632 |    0.893  |   0.5857 |        0.1259 |            0.8759 |           0.0067 |                  25.031 |

## Visualizations

- ROC curves: `figures/roc_curves.png`
- Precision-Recall curves: `figures/pr_curves.png`
- Calibration curves: `figures/calibration_curves.png`
- Metric comparison bar chart: `figures/metric_comparison_bars.png`

## Explainability Compatibility Notes

- **High interpretability** (Logistic Regression, Decision Tree): coefficients/tree splits are directly readable; SHAP `LinearExplainer`/`TreeExplainer` both apply cleanly.
- **Medium interpretability** (Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost): not directly readable, but all are tree-based ensembles fully compatible with SHAP `TreeExplainer` (exact, fast Shapley values) — verified in Milestone 12.
