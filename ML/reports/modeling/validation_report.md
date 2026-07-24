# Reproducibility & Validation Report

Generated: 2026-07-24T19:42:49.969720+00:00

## Overall: PASS

## Retrain Determinism

```
{'passed': True, 'model_name': 'lightgbm', 'max_abs_diff': 0.0}
```

## End-to-End Smoke Test (raw row -> PreprocessingPipeline -> model -> prediction)

```
{'passed': True, 'sample_predictions': [0.0006513911947187571, 0.0011353157575940025, 0.00047805344328055136]}
```

## Unit Tests

See `ML/tests/` (`pytest ML/tests`) for module-level unit tests covering metrics, cross-validation, survey-aware modeling, and the full preprocessing pipeline.
