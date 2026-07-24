# Validation Report

Generated: 2026-07-24T15:37:34.539254+00:00

## [PASS] expected_shape

Expected 16025 rows x 913 columns, found 16025 rows x 913 columns.

## [PASS] target_variables_present

All required columns are present.

```
{
  "missing_columns": []
}
```

## [PASS] survey_variables_present

All required columns are present.

```
{
  "missing_columns": []
}
```

## [PASS] duplicate_rows

0 fully duplicate row(s) found (informational; no rows removed).

```
{
  "duplicate_count": 0
}
```

## [PASS] missing_values_summary

0 column(s) are 100% missing. Top 15 columns by missing percentage recorded in details.

```
{
  "fully_missing_columns": [],
  "top_missing_percentage": {
    "PRESCR30": 99.99,
    "COMSTAT30": 99.99,
    "CONTSUB30": 99.99,
    "COMSTAT29": 99.97,
    "CONTSUB29": 99.97,
    "PRESCR29": 99.97,
    "CONTSUB28": 99.93,
    "COMSTAT28": 99.93,
    "PRESCR28": 99.93,
    "CONTSUB27": 99.91,
    "COMSTAT27": 99.91,
    "PRESCR27": 99.91,
    "COMSTAT26": 99.88,
    "CONTSUB26": 99.88,
    "PRESCR26": 99.88
  }
}
```

## [PASS] target_distribution

Target variable value distributions recorded in details.

```
{
  "ADMITHOS": {
    "0.0": 13904,
    "1.0": 2121
  },
  "OBSHOS": {
    "0.0": 15848,
    "1.0": 177
  },
  "derived_hospital_admission": {
    "0": 13904,
    "1": 2121
  }
}
```
