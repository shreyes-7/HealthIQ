"""Standardizes free-text categorical codes (diagnosis/medication/cause
codes, arrival time strings): strips surrounding whitespace and
uppercases, so values compare consistently downstream.

Milestone 3 investigation confirmed no blank/whitespace-only strings
exist anywhere in this dataset today; this is a defensive standardization
pass for future data releases, not a fix for a known issue in this one.
"""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog


def standardize_string_columns(
    dataframe: pd.DataFrame, string_columns: list[str], transformation_log: TransformationLog
) -> pd.DataFrame:
    cleaned = dataframe.copy()

    for column in string_columns:
        series = cleaned[column]
        standardized = series.str.strip().str.upper()

        changed_count = int((standardized != series).fillna(False).sum())
        cleaned[column] = standardized

        if changed_count > 0:
            transformation_log.record(
                "standardize_text", column, "stripped_and_uppercased", count=changed_count
            )

    return cleaned
