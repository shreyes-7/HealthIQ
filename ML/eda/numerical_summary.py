"""Numerical summary statistics and IQR-based outlier analysis.

Read-only: statistics are computed for reporting only, nothing is changed
or removed from the dataset.

Important caveat: many NHAMCS numeric fields use negative sentinel codes
(commonly -7 = Not applicable, -8 = Unknown, -9 = Blank) rather than a
missing value. Summary statistics such as mean/std/min are computed on the
raw values and will be distorted wherever a column uses these codes. The
`negative_value_count` column below flags this so it can be addressed
during Milestone 4 (Data Cleaning); no recoding happens here.
"""

import pandas as pd

OUTLIER_IQR_MULTIPLIER = 1.5


def _summarize_column(dataframe: pd.DataFrame, column: str) -> dict:
    non_null = dataframe[column].dropna()
    record = {"variable_name": column, "count": int(non_null.shape[0])}

    if non_null.empty:
        record.update(
            {
                "mean": None, "std": None, "min": None, "p25": None, "median": None,
                "p75": None, "max": None, "negative_value_count": 0,
                "negative_value_percentage": None, "iqr_lower_bound": None,
                "iqr_upper_bound": None, "outlier_count": 0, "outlier_percentage": None,
            }
        )
        return record

    q1 = non_null.quantile(0.25)
    q3 = non_null.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - OUTLIER_IQR_MULTIPLIER * iqr
    upper_bound = q3 + OUTLIER_IQR_MULTIPLIER * iqr
    outlier_count = int(((non_null < lower_bound) | (non_null > upper_bound)).sum())
    negative_count = int((non_null < 0).sum())

    record.update(
        {
            "mean": round(non_null.mean(), 3),
            "std": round(non_null.std(), 3),
            "min": non_null.min(),
            "p25": q1,
            "median": non_null.median(),
            "p75": q3,
            "max": non_null.max(),
            "negative_value_count": negative_count,
            "negative_value_percentage": round(negative_count / non_null.shape[0] * 100, 2),
            "iqr_lower_bound": round(lower_bound, 3),
            "iqr_upper_bound": round(upper_bound, 3),
            "outlier_count": outlier_count,
            "outlier_percentage": round(outlier_count / non_null.shape[0] * 100, 2),
        }
    )
    return record


def build_numerical_summary(dataframe: pd.DataFrame, numerical_columns: list[str]) -> pd.DataFrame:
    records = [_summarize_column(dataframe, column) for column in numerical_columns]
    return pd.DataFrame.from_records(records)
