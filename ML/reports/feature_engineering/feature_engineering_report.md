# Feature Engineering Report

Generated: 2026-07-24T17:41:18.297010+00:00

- Input (cleaned) shape: 16025 rows x 801 columns
- Output feature matrix: 16025 rows x 852 columns
- Target column: `hospital_admission` (derived from `ADMITHOS`/`OBSHOS`, both removed from features)
- Output file: `Data/processed/ed2022_model_ready.parquet`
- No model was trained. Cleaned dataset (`ed2022_cleaned.parquet`) and raw dataset were not modified.

## 1. Leakage, Facility-Level, and Identifier Exclusion

53 columns excluded from the feature set before encoding:

- **Disposition block** (16 vars) and **post-admission hospital course** (14 vars): these describe the admission decision itself or its downstream consequences (which unit, length of stay, discharge diagnosis, boarding time) — using them as predictors would leak the answer into the input.
- **Facility-level questionnaire items** (16 vars): hospital-level policy/staffing questions (ambulance diversion, bed coordinators), not per-visit clinical data.
- **Identifiers** (`HOSPCODE`, `PATCODE`): kept in the output for traceability but excluded from the feature matrix — an ID number is never a valid predictor.
- **Survey variables** (`PATWT`, `EDWT`, `CSTRATM`, `CPSUM`): preserved untouched in the output, excluded from the feature matrix — see Milestone 1/3 for why.
- **`AGEDAYS`**: legitimate pre-decision variable but 97%+ missing outside the infant subgroup and largely redundant with `AGE`.

Full list: `ML/reports/feature_engineering/feature_roles.json`.

## 2. Redundant Variable Removal

- Dropped `['RFV3', 'RFV4', 'RFV2', 'RFV5', 'RFV1']` (correlation 1.0 with their `*3D` recode per Milestone 2 EDA); kept the coarser 3-digit recode for tractable, interpretable encoding.
- Dropped 359 near-zero-variance categorical columns (dominant category >= 99% of visits — mostly rarely-used medication-slot fields). Full list in `feature_roles.json`. More rigorous, target-aware feature selection is deferred to Milestone 6.

## 3. Categorical Encoding

- One-hot encoded (<= 15 categories): 232 variables (most-frequent category dropped as reference to avoid the dummy-variable trap)
- Frequency encoded (> 15 categories): 138 variables (diagnosis/drug/arrival-time codes — one-hot would add thousands of near-empty columns)

## 4. Numerical Scaling

- Z-score standardized: 20 continuous variables (['AGE', 'BPDIAS', 'BPDIASD', 'BPSYS', 'BPSYSD', 'LOV', 'NUMDIS', 'NUMGIV', 'NUMMED', 'POPCT', 'PULSE', 'PULSED', 'PULSE_PRESSURE', 'RESPR', 'RESPRD', 'SHOCK_INDEX', 'TEMPDF', 'TEMPF', 'TOTDIAG', 'WAITTIME'])
- Not applied to encoded categorical/boolean columns (they remain 0/1 indicators).
- Tree-based models (Random Forest, XGBoost, LightGBM, CatBoost) do not require scaling; it is provided for Logistic Regression and saved as a reusable artifact. Raw values remain available in `ed2022_cleaned.parquet`; mean/std per column are in `ML/saved_models/metadata.json` for inverse-transform.

## 5. Final Feature Matrix

- 852 total feature columns (20 scaled continuous + encoded categoricals)

## 6. Reproducibility Caveat

The encoder and scaler in this milestone are fit on the **full** cleaned dataset, because Milestone 7 (Train/Test Split) had not yet run when this script was first written. Milestone 9's `ML/pipeline/preprocessing_pipeline.py` now exposes a proper `fit`/`transform` contract so the same encoder/scaler can be refit on a training split only and reapplied to test/inference data without leaking test-set statistics — see that module for the reusable entry point.
