# Train/Test Preparation Report

Generated: 2026-07-24T17:42:14.842073+00:00

Split ratios: train 70% / validation 15% / test 15%, stratified by the prediction target, random_state=42.

The split happens on the RAW dataset, before cleaning or feature engineering. The PreprocessingPipeline is fit ONLY on the training split; validation and test are transformed using that fitted state (learned imputation medians, dropped-column decisions, encoder categories, scaler mean/std) — never re-derived from validation/test data. This is what makes the split methodologically valid: no information from held-out rows leaks into how the training data was preprocessed.

## Split sizes and class balance

| Split | Rows | Not Admitted | Admitted | % Admitted |
|---|---|---|---|---|
| train | 11217 | 9732 | 1485 | 13.24% |
| validation | 2404 | 2086 | 318 | 13.23% |
| test | 2404 | 2086 | 318 | 13.23% |

Feature schema identical across all three splits: **True** (866 feature columns).

## Output files

- `Data/processed/train.parquet`
- `Data/processed/validation.parquet`
- `Data/processed/test.parquet`
- `ML/saved_models/preprocessing_pipeline.pkl`, `encoder.pkl`, `scaler.pkl`, `preprocessing.pkl`, `feature_names.json`, `metadata.json` — all now fit on the **training split only** (superseding the full-dataset-fit versions produced in Milestones 4/5/9).

## No model was trained

Only the preprocessing pipeline (cleaning + feature engineering state) was fit on the training split. No predictive model was trained or evaluated.
