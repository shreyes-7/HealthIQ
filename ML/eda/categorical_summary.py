"""Categorical summary statistics: cardinality, top categories, rare categories.

Read-only: no categories are collapsed, recoded, or removed here.
"""

import pandas as pd

RARE_CATEGORY_THRESHOLD_PERCENT = 1.0
TOP_CATEGORIES_TO_REPORT = 5


def _summarize_column(dataframe: pd.DataFrame, column: str) -> dict:
    series = dataframe[column]
    non_null = series.dropna()
    total = non_null.shape[0]
    missing_count = int(series.isna().sum())

    record = {
        "variable_name": column,
        "n_unique": int(series.nunique(dropna=True)),
        "missing_count": missing_count,
        "missing_percentage": round(missing_count / len(series) * 100, 2),
    }

    if total == 0:
        record.update({"top_values": "", "rare_category_count": 0})
        return record

    value_counts = non_null.value_counts()
    value_percentages = value_counts / total * 100

    top_values = value_counts.head(TOP_CATEGORIES_TO_REPORT)
    record["top_values"] = "; ".join(
        f"{value}={count} ({round(value_percentages[value], 1)}%)"
        for value, count in top_values.items()
    )
    record["rare_category_count"] = int((value_percentages < RARE_CATEGORY_THRESHOLD_PERCENT).sum())

    return record


def build_categorical_summary(dataframe: pd.DataFrame, categorical_columns: list[str]) -> pd.DataFrame:
    records = [_summarize_column(dataframe, column) for column in categorical_columns]
    return pd.DataFrame.from_records(records)
