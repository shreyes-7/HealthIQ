# Datetime and Identifier Variables

Completes the two open Milestone 2 sub-tasks not covered by earlier reports.

## Datetime Variables

The raw dataset contains **no true datetime-typed columns**. Time-related
information is present but stored as coded/formatted fields, not parseable
timestamps:

| Variable | Format | Why it isn't a datetime |
|---|---|---|
| `VMONTH` | 1-12 | Month recode (categorical), no year/day component |
| `VDAYR` | 1-7 | Day-of-week recode (categorical), no calendar date |
| `ARRTIME` | 4-digit zero-padded military time string (e.g. `"0604"`) | Time-of-day only, no date; kept as a string category (see `ML/cleaning/standardize_text.py`) since a full arrival timestamp cannot be reconstructed (no arrival date field exists in the public-use file — NCHS withholds exact visit dates for disclosure-avoidance reasons) |
| `WAITTIME`, `LOV`, `LOS`, `OBSSTAY`, `BOARDED` | Integer duration (minutes/days) | Durations, not points in time — already handled as continuous numerical variables |

No column was reclassified or converted as a result of this review; this
documents that the absence of a datetime dtype in `dataset_report.md`'s
dtype breakdown is expected, not an oversight.

## Identifier Variables

Two columns are patient/facility identifiers rather than measurements or
categories, confirmed against the codebook (Milestone 3 investigation):

| Variable | Description | Range |
|---|---|---|
| `HOSPCODE` | Hospital identifier (masked/re-coded by NCHS for disclosure avoidance) | 1-188 |
| `PATCODE` | Patient identifier, unique only within a given hospital | 1-173 |

These are defined in `ML.cleaning.variable_roles.IDENTIFIER_VARIABLES` and
have been excluded from every statistical/modeling treatment since
Milestone 3: no sentinel conversion, no imputation, no encoding, no
scaling. They are carried through the cleaned dataset and the feature-
engineered output purely for traceability (e.g. grouping visits by
hospital) and are excluded from the model-ready feature matrix built by
`ML.feature_engineering.pipeline` (see `ML/reports/feature_engineering/feature_roles.json`,
role `excluded_identifier_kept_for_traceability`).
