# SHAP Integration Report

Generated: 2026-07-25T08:12:59.089836+00:00

- Model: `LGBMClassifier` (family: `tree`)
- Explainer: `TreeExplainer`
- Explained dataset: validation split (held-out, unseen during training)
- SHAP values shape: (2404, 866) (rows x features)
- Runtime: 12.84s total, 0.0053s/row
- Expected value (base rate, margin/log-odds space): -8.3047

## Verification

- Output dimensions match (n_validation_rows, n_features) exactly.
- SHAP values are in **margin (log-odds) space**, not probability space (`ML.explainability.shap_utils.sigmoid` converts for human-readable output). Confirmed empirically: `shap_values.sum(axis=1) + expected_value` reconstructs `model.predict(X, raw_score=True)` to within 3e-9, and its sigmoid reconstructs `predict_proba` exactly. Full reproduction check with tolerances is Milestone 7.

## Saved Artifacts

- `ML/saved_models/shap_explainer.pkl` — the fitted explainer, reusable without rebuilding
- `ML/reports/explainability/shap_values_validation.npy` — computed values, reusable without recomputing (Milestones 3, 5, 6, 7 load this directly)