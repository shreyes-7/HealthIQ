"""Classifies each variable as numerical or categorical for EDA purposes.

Heuristic: any string-typed column is categorical. A numeric (float64)
column is treated as categorical when it has few enough distinct values to
plausibly represent a coded/discrete variable rather than a continuous
measurement.

This is an approximation. NHAMCS stores both continuous measurements and
small-integer codes as the same dtype, and confirming the true semantics of
all 913 variables individually would require the per-variable codebook for
each one. The threshold below was checked against known variables (e.g.
AGER, SEX, IMMEDR are correctly categorical; AGE, PULSE, BPSYS are
correctly numerical) and is documented here rather than hidden.
"""

import pandas as pd

CATEGORICAL_MAX_UNIQUE = 20


def classify_variable_type(series: pd.Series) -> str:
    if pd.api.types.is_string_dtype(series) or series.dtype == object:
        return "categorical"
    if series.nunique(dropna=True) <= CATEGORICAL_MAX_UNIQUE:
        return "categorical"
    return "numerical"


def split_columns_by_type(dataframe: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Return (numerical_columns, categorical_columns)."""
    numerical_columns = []
    categorical_columns = []

    for column in dataframe.columns:
        if classify_variable_type(dataframe[column]) == "numerical":
            numerical_columns.append(column)
        else:
            categorical_columns.append(column)

    return numerical_columns, categorical_columns
