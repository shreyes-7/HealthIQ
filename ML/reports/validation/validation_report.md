# Validation Report (Milestone 11)

Generated: 2026-07-24T17:43:13.991898+00:00

## Overall: PASS

### [PASS] no_missing_values_in_features

```
{'passed': True, 'detail': {'train': {'passed': True, 'missing_cells': 0}, 'validation': {'passed': True, 'missing_cells': 0}, 'test': {'passed': True, 'missing_cells': 0}}}
```

### [PASS] correct_datatypes

```
{'passed': True, 'detail': {'train': {'passed': True, 'non_numeric_columns': []}, 'validation': {'passed': True, 'non_numeric_columns': []}, 'test': {'passed': True, 'non_numeric_columns': []}}}
```

### [PASS] correct_feature_dimensions

```
{'passed': True, 'per_split_matches_train': {'train': True, 'validation': True, 'test': True}, 'feature_count': 866}
```

### [PASS] pipeline_reproducibility

```
{'passed': True, 'features_match': True, 'target_match': True}
```

## Pipeline unit tests

Automated unit tests for the individual modules (sentinel handling, leakage exclusion, encoder/scaler fit-transform correctness, derived features, cleaning/feature-engineering fit-vs-transform consistency) are in `ML/tests/` — run with `pytest ML/tests`.
