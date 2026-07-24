"""Duplicate row analysis. Read-only: no rows are removed."""

import pandas as pd


def analyze_duplicates(dataframe: pd.DataFrame) -> dict:
    is_duplicate = dataframe.duplicated(keep="first")
    duplicate_row_count = int(is_duplicate.sum())

    return {
        "duplicate_row_count": duplicate_row_count,
        "duplicate_row_percentage": round(duplicate_row_count / len(dataframe) * 100, 4),
        "duplicate_row_indices": dataframe.index[is_duplicate].tolist(),
    }
