# Exploratory Data Analysis Report

Generated: 2026-07-24T15:54:03.442243+00:00

Dataset shape: 16025 rows x 913 columns.
Classified as 37 numerical and 876 categorical variables (see `ML/eda/type_classification.py` for the classification rule).

## 1. Missing Value Analysis

- Total missing cells: 1,325,889 / 14,630,825 (9.0623%)
- Columns with no missing values: 822
- Columns with more than 50% missing: 85
- Fully missing columns: none
- Full per-variable detail: `missing_values_report.csv`
- Heatmap (top 30 columns by missing %): `figures/missing_value_heatmap.png`

## 2. Duplicate Analysis

- Fully duplicate rows: 0 (0.0%)

## 3. Numerical Summaries

Per-variable count, mean, std, min/p25/median/p75/max, negative-sentinel-code count, and IQR-based outlier count: `numerical_summary.csv`.

**Important caveat:** NHAMCS commonly encodes Not-applicable/Unknown/Blank as negative sentinel values (e.g. -7, -8, -9) rather than as NaN. These distort mean/std/outlier statistics wherever they occur — see the `negative_value_count` column. No recoding is performed at this stage (deferred to Milestone 4).

## 4. Categorical Summaries

Per-variable cardinality, missing percentage, top 5 categories, and rare-category count (categories under 1% frequency): `categorical_summary.csv`.

## 5. Class Imbalance Analysis

Target: `['0', '1']` derived as `ADMITHOS == 1 or OBSHOS == 1` (see Milestone 1's target_and_survey_variables.md).

- Counts: {'0': 13904, '1': 2121}
- Percentages: {'0': 86.76, '1': 13.24}
- Imbalance ratio (majority:minority): 6.56:1
- Plot: `figures/target_class_distribution_bar.png`

## 6. Correlation Analysis

- Full numerical correlation matrix: `correlation_matrix.csv`
- Variable pairs with |correlation| >= 0.7: `top_correlated_pairs.csv` (13 found)
- Numerical variables ranked by correlation with the target: `target_correlation.csv`
- Heatmap of key numerical variables: `figures/correlation_heatmap.png`

## 7. Outlier Analysis

IQR-based outlier counts (1.5x IQR beyond Q1/Q3) are included per variable in `numerical_summary.csv` (`outlier_count` / `outlier_percentage` columns). Note the negative-sentinel-code caveat above — some flagged outliers are Not-applicable/Unknown codes rather than genuine extreme values.

## 8. Distribution Plots

Plotted for 21 of 21 curated key variables (clinically meaningful vitals, demographics, and visit characteristics) plus the target. The remaining ~890 columns are administrative/free-text-coded fields already fully profiled in the summary CSVs above; plotting all of them individually was judged low value and was intentionally out of scope for this report.

Numerical: `figures/age_histogram.png`, `figures/waittime_histogram.png`, `figures/lov_histogram.png`, `figures/tempf_histogram.png`, `figures/pulse_histogram.png`, `figures/respr_histogram.png`, `figures/bpsys_histogram.png`, `figures/bpdias_histogram.png`, `figures/popct_histogram.png`, `figures/boarded_histogram.png`

Categorical: `figures/sex_bar.png`, `figures/ager_bar.png`, `figures/racer_bar.png`, `figures/ethun_bar.png`, `figures/arrems_bar.png`, `figures/paytyper_bar.png`, `figures/immedr_bar.png`, `figures/painscale_bar.png`, `figures/vdayr_bar.png`, `figures/vmonth_bar.png`, `figures/stay24_bar.png`

## Key Findings

- `LOS` has the strongest correlation with the target (0.817).
  `LOS` (length of hospital stay) is a leakage risk rather than a usable predictor: it is only populated for already-admitted visits (sentinel-coded otherwise) and is not known at the time an admission decision would be predicted. Flag for exclusion in Milestone 5/6.
- Near-perfectly correlated pairs found: `RFV1`/`RFV13D`, `RFV3`/`RFV33D`, `RFV2`/`RFV23D`, `RFV4`/`RFV43D`, `RFV5`/`RFV53D`. These likely represent duplicate or recoded/derived versions of the same underlying item and are candidates for redundancy removal in Milestone 6 (Feature Selection).
