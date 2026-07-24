# Data Cleaning Report

Generated: 2026-07-24T17:41:15.043081+00:00

- Raw shape: 16025 rows x 913 columns
- Cleaned shape: 16025 rows x 801 columns
- Output: `Data/processed/ed2022_cleaned.parquet`
- Raw file (`Data/raw/ed2022_sas.sas7bdat`) was not modified.

## 1. Duplicate Removal

- Duplicate rows removed: 0
- Duplicate columns removed: 100 (RX1V3C4 (dup of RX1CAT4), RX3V3C4 (dup of RX3CAT4), RX5V3C4 (dup of RX5CAT4), RX6V3C4 (dup of RX6CAT4), RX7V3C4 (dup of RX7CAT4), RX8V3C4 (dup of RX8CAT4), RX9V3C4 (dup of RX9CAT4), RX10V3C4 (dup of RX10CAT4), RX11V3C4 (dup of RX11CAT4), RX12V3C4 (dup of RX12CAT4), RX13V3C4 (dup of RX13CAT4), RX14V3C4 (dup of RX14CAT4), RX15V3C4 (dup of RX15CAT4), RX16V1C4 (dup of RX16CAT4), RX16V2C4 (dup of RX16CAT4), RX16V3C4 (dup of RX16CAT4), RX17CAT4 (dup of RX16CAT4), RX17V1C4 (dup of RX16CAT4), RX17V2C4 (dup of RX16CAT4), RX17V3C4 (dup of RX16CAT4), RX18CAT4 (dup of RX16CAT4), RX18V1C4 (dup of RX16CAT4), RX18V2C4 (dup of RX16CAT4), RX18V3C4 (dup of RX16CAT4), RX19CAT4 (dup of RX16CAT4), RX19V1C4 (dup of RX16CAT4), RX19V2C4 (dup of RX16CAT4), RX19V3C4 (dup of RX16CAT4), RX20CAT4 (dup of RX16CAT4), RX20V1C4 (dup of RX16CAT4), RX20V2C4 (dup of RX16CAT4), RX20V3C4 (dup of RX16CAT4), RX21V3C3 (dup of RX16CAT4), RX22CAT4 (dup of RX16CAT4), RX22V1C4 (dup of RX16CAT4), RX22V2C4 (dup of RX16CAT4), RX22V3C4 (dup of RX16CAT4), RX23CAT4 (dup of RX16CAT4), RX23V1C4 (dup of RX16CAT4), RX23V2C4 (dup of RX16CAT4), RX23V3C4 (dup of RX16CAT4), RX25CAT4 (dup of RX16CAT4), RX25V1C4 (dup of RX16CAT4), RX25V2C4 (dup of RX16CAT4), RX25V3C3 (dup of RX16CAT4), RX25V3C4 (dup of RX16CAT4), RX26CAT3 (dup of RX16CAT4), RX26CAT4 (dup of RX16CAT4), RX26V1C3 (dup of RX16CAT4), RX26V1C4 (dup of RX16CAT4), RX26V2C3 (dup of RX16CAT4), RX26V2C4 (dup of RX16CAT4), RX26V3C3 (dup of RX16CAT4), RX26V3C4 (dup of RX16CAT4), RX28CAT3 (dup of RX16CAT4), RX28CAT4 (dup of RX16CAT4), RX28V1C3 (dup of RX16CAT4), RX28V1C4 (dup of RX16CAT4), RX28V2C3 (dup of RX16CAT4), RX28V2C4 (dup of RX16CAT4), RX28V3C3 (dup of RX16CAT4), RX28V3C4 (dup of RX16CAT4), RX29CAT2 (dup of RX16CAT4), RX29CAT3 (dup of RX16CAT4), RX29CAT4 (dup of RX16CAT4), RX29V1C2 (dup of RX16CAT4), RX29V1C3 (dup of RX16CAT4), RX29V1C4 (dup of RX16CAT4), RX29V2C2 (dup of RX16CAT4), RX29V2C3 (dup of RX16CAT4), RX29V2C4 (dup of RX16CAT4), RX29V3C2 (dup of RX16CAT4), RX29V3C3 (dup of RX16CAT4), RX29V3C4 (dup of RX16CAT4), RX30CAT3 (dup of RX16CAT4), RX30CAT4 (dup of RX16CAT4), RX30V1C3 (dup of RX16CAT4), RX30V1C4 (dup of RX16CAT4), RX30V2C3 (dup of RX16CAT4), RX30V2C4 (dup of RX16CAT4), RX30V3C1 (dup of RX16CAT4), RX30V3C2 (dup of RX16CAT4), RX30V3C3 (dup of RX16CAT4), RX30V3C4 (dup of RX16CAT4), RX17V3C3 (dup of RX17CAT3), RX19V3C3 (dup of RX19CAT3), RX20V3C3 (dup of RX20CAT3), RX21V2C3 (dup of RX21CAT3), RX21V3C4 (dup of RX21CAT4), RX22V3C3 (dup of RX22CAT3), RX23V3C3 (dup of RX23CAT3), RX24V3C3 (dup of RX24CAT3), RX24V3C4 (dup of RX24CAT4), RX25V2C3 (dup of RX25CAT3), RX27V3C3 (dup of RX27CAT3), RX27V3C4 (dup of RX27CAT4), COMSTAT30 (dup of PRESCR30), RX30V2C1 (dup of RX30CAT1), RX30V2C2 (dup of RX30CAT2), RX30V1C2 (dup of RX30V1C1))

## 2. Constant Column Removal

- Constant (single-value) columns removed: 12

## 3. Sentinel / Invalid Value Handling

NHAMCS encodes Not-applicable (-7), Unknown (-8), and Blank (-9) as sentinel codes rather than true NaN, in both numeric and string-typed columns (confirmed by a full-dataset scan; no other negative codes or blank strings exist). All were converted to proper NaN.

- Columns with sentinel codes converted: 166
- Total sentinel values converted to NaN: 1514934

Codebook-documented non-numeric annotation codes were also converted to NaN (e.g. `PULSE`/`PULSED` == 998 means "measured by Doppler", not a heart rate of 998; same for `BPDIAS`/`BPDIASD`):

- `PULSE`: 88 annotation code(s) ([998]) converted to NaN
- `PULSED`: 3 annotation code(s) ([998]) converted to NaN
- `BPDIAS`: 1 annotation code(s) ([998]) converted to NaN

## 4. Implied-Decimal Corrections

The codebook documents an implied decimal for these variables (e.g. `TEMPF` raw value 986 means 98.6°F; `RFV1-5` raw codes are the real code x10). Values were divided by 10 accordingly:

- `RFV2`: 10220 value(s) corrected
- `RFV5`: 2106 value(s) corrected
- `RFV3`: 6434 value(s) corrected
- `TEMPF`: 15088 value(s) corrected
- `RFV1`: 16000 value(s) corrected
- `TEMPDF`: 4756 value(s) corrected
- `RFV4`: 3822 value(s) corrected

## 5. Data Type Corrections

- Genuine 0/1 flags converted to a 2-level "No"/"Yes" category.
- Identifier columns (`HOSPCODE`, `PATCODE`) converted to nullable Int64; never treated as a measurement.
- Whole-number continuous/conditional variables converted to nullable Int64; decimal measurements (`TEMPF`, `TEMPDF`, RFV codes) remain float64.
- RFV nominal codes converted to category dtype (median imputation on a classification code is meaningless).
- All remaining generic categorical columns converted to category dtype.

## 6. Missing Value Imputation

- Continuous numerical variables median-imputed: 14
  - `RESPR`: 856 value(s) filled with median 18.0
  - `BPSYSD`: 9334 value(s) filled with median 128.0
  - `BPDIASD`: 9339 value(s) filled with median 75.0
  - `PULSED`: 9021 value(s) filled with median 81.0
  - `LOV`: 697 value(s) filled with median 191.0
  - `BPDIAS`: 1754 value(s) filled with median 78.0
  - `TEMPF`: 937 value(s) filled with median 98.1
  - `WAITTIME`: 2753 value(s) filled with median 14.0
  - `TEMPDF`: 11269 value(s) filled with median 98.2
  - `POPCT`: 969 value(s) filled with median 98.0
  - `TOTDIAG`: 225 value(s) filled with median 3.0
  - `PULSE`: 1053 value(s) filled with median 88.0
  - `RESPRD`: 9253 value(s) filled with median 18.0
  - `BPSYS`: 1722 value(s) filled with median 131.0

- Conditional numerical variables deliberately left as NaN (value does not conceptually apply to most rows):
  - `AGEDAYS`: 15597 NaN remaining (not imputed) — value is only defined for a subset of visits (codebook sentinel -7 = Not applicable)
  - `OBSSTAY`: 15700 NaN remaining (not imputed) — value is only defined for a subset of visits (codebook sentinel -7 = Not applicable)
  - `BOARDED`: 14352 NaN remaining (not imputed) — value is only defined for a subset of visits (codebook sentinel -7 = Not applicable)
  - `LOS`: 14002 NaN remaining (not imputed) — value is only defined for a subset of visits (codebook sentinel -7 = Not applicable)

- Categorical columns filled with an explicit "Missing" category: 228
  (chosen over mode-imputation so unknown/blank/not-applicable remains visible to downstream models rather than being folded into the majority class)

## 7. Survey Variables

`['CPSUM', 'CSTRATM', 'EDWT', 'PATWT']` were never touched by any step above — preserved exactly as in the raw dataset for the survey-aware learning workflow.

## 8. Remaining Missing Values

After cleaning, missing values remain only in conditional numerical variables (by design) and `EDWT` (genuine facility non-participation, not sentinel-coded — see Milestone 1).

- `EDWT`: 15837 (98.83%)
- `OBSSTAY`: 15700 (97.97%)
- `AGEDAYS`: 15597 (97.33%)
- `BOARDED`: 14352 (89.56%)
- `LOS`: 14002 (87.38%)