# Explanation Validation Report

Generated: 2026-07-25T09:58:42.850947+00:00

## Overall: VALID

## Checks

### [PASS] `shap_values_reproduce_predictions`

- max_abs_diff: `1.5544114329024694e-09`
- tolerance: `1e-06`
- n_rows_checked: `2404`

### [PASS] `feature_ordering_consistency`

- shap_values_column_count: `866`
- feature_names_count: `866`
- features_dataframe_order_matches: `True`

### [PASS] `explanation_stability`

- max_abs_diff_between_two_runs: `0.0`
- n_rows_checked: `100`

### [PASS] `no_missing_shap_values`

- nan_count: `0`
- total_values: `2081864`

### [PASS] `no_preprocessing_mismatch`

- schema_matches: `True`
- model_predicts_successfully: `True`
- n_rows_checked: `100`

## Limitations

- `shap_values_reproduce_predictions` and `no_missing_shap_values` were checked on the full validation split (2,404 rows); `explanation_stability` and `no_preprocessing_mismatch` were checked on smaller samples (100 rows each) for runtime reasons — TreeExplainer's determinism is a property of the algorithm (exact tree-path-dependent computation, no sampling), not data-dependent, so a small sample is sufficient to catch a configuration problem if one existed.
- These checks validate SHAP's **internal mathematical consistency** with the model (values sum correctly, ordering is stable, nothing is missing) and the **preprocessing handoff** (raw data still transforms into the exact schema the model expects). They do NOT validate that the underlying model itself is clinically correct or unbiased — that is a separate, ongoing concern addressed partially by the clinical-plausibility cross-checks in Milestones 3 and 6, not resolved by this milestone alone.