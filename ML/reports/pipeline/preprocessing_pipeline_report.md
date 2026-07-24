# Preprocessing Pipeline Report

Generated: 2026-07-24T16:53:33.883143+00:00

## What this milestone consolidates

`ML/pipeline/preprocessing_pipeline.py` wraps the previously-separate Milestone 1 (ingestion), Milestone 3 (cleaning), and Milestone 4 (feature engineering) modules behind a single `PreprocessingPipeline` class with a `fit_transform`/`transform` contract:

1. **Load** raw data — `ML.ingestion.loader.load_dataset`
2. **Validate** — `ML.ingestion.validator.run_all_validations` (raises on failure via `load_validate_and_fit`, rather than silently preprocessing invalid data)
3. **Clean** — `ML.cleaning.pipeline.fit_clean_dataset` / `transform_clean_dataset`
4. **Engineer features (encode + scale)** — `ML.feature_engineering.pipeline.fit_engineer_features` / `transform_engineer_features`
5. **Preserve survey variables** — `PATWT`/`EDWT`/`CSTRATM`/`CPSUM` pass through every stage untouched

## Why fit/transform, not just one function

Milestones 3 and 4 originally detected-and-applied cleaning/encoding decisions in a single pass. That is fine for a one-off report, but is NOT reusable: calling the same code again on a different dataset (a validation split, or a future inference request) would silently recompute different imputation medians, a different dropped-column list, and different encoder categories — violating the requirement (CLAUDE.md, PROJECT_CONTEXT.md) that preprocessing at inference time exactly match preprocessing at training time.

This milestone split the genuinely data-dependent decisions (duplicate/constant/near-zero-variance columns to drop, which columns are boolean, imputation medians, encoder categories, scaler mean/std) out from the stateless rules (sentinel codes, implied-decimal correction, text standardization, leakage exclusion, target derivation), so the former can be learned once and reapplied consistently.

## Reproducibility check

Running the full pipeline directly from the raw SAS file reproduced a 16025 x 850 output — matching the shape independently produced by the separate Milestone 3 + 4 scripts.

## Reusability smoke test

Fit on the first 80% of raw rows, then called `transform()` on the remaining 20% (an ad hoc slice for this test only — not the official Milestone 7 train/test split):

- Fit slice: 12820 rows -> 853 feature columns
- Transform slice: 3205 rows -> 853 feature columns
- Feature schema identical between fit and transform outputs: **True**

This confirms `transform()` reuses the fitted encoder/scaler/medians/dropped-column-lists rather than re-deriving them from the new slice — the core property a 'reusable' pipeline requires.

## Persisted artifacts

- `ML/saved_models/preprocessing_pipeline.pkl` — the full fitted `PreprocessingPipeline` object (reload with `PreprocessingPipeline.load(...)`)
- `ML/saved_models/encoder.pkl`, `scaler.pkl`, `preprocessing.pkl` — individually loadable, matching TASKS.md's prescribed `saved_models/` layout
- `ML/saved_models/feature_names.json`, `metadata.json`

## No model was trained

Only preprocessing artifacts (encoder, scaler, imputation medians, dropped-column lists) were fit and persisted — no predictive model (Logistic Regression, Random Forest, etc.) was trained, per PROJECT_CONTEXT.md's Machine Learning / Backend separation of concerns.
