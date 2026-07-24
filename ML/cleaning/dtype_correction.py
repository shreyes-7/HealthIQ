"""Corrects pandas dtypes so they reflect the true nature of each variable.

Run this AFTER sentinel conversion, non-numeric-annotation conversion, and
implied-decimal correction, so dtype decisions are based on final values.

- Genuine 0/1 flags become a 2-level "No"/"Yes" category (boolean semantics
  made explicit and human-readable, instead of opaque 0.0/1.0 floats).
- Remaining generic categorical columns (from the EDA numerical/categorical
  split, excluding the special numeric roles) become pandas "category"
  dtype. Whole-number float columns are cast to nullable Int64 first so
  category labels read "1"/"2" rather than "1.0"/"2.0".
- Identifier columns become nullable Int64 (still not treated as a
  measurement or a category to impute).
- Whole-number continuous/conditional numeric columns become nullable
  Int64; genuine decimal measurements (TEMPF/TEMPDF after unit correction)
  stay float64.
"""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.variable_roles import (
    CONDITIONAL_NUMERICAL_VARIABLES,
    CONTINUOUS_NUMERICAL_VARIABLES,
    IDENTIFIER_VARIABLES,
    NOMINAL_CODE_VARIABLES,
    SURVEY_VARIABLES,
    get_all_special_role_columns,
)

BOOLEAN_LABELS = {0: "No", 1: "Yes"}


def _is_whole_number_column(series: pd.Series) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return False
    return (non_null % 1 == 0).all()


def detect_boolean_columns(dataframe: pd.DataFrame) -> list[str]:
    """Columns (outside the special numeric roles) whose only non-null
    values are 0 and/or 1."""
    excluded = get_all_special_role_columns()
    boolean_columns = []

    for column in dataframe.columns:
        if column in excluded:
            continue

        series = dataframe[column]
        if not pd.api.types.is_numeric_dtype(series):
            continue

        non_null_values = set(series.dropna().unique())
        if non_null_values and non_null_values.issubset({0, 1}):
            boolean_columns.append(column)

    return boolean_columns


def convert_boolean_columns(
    dataframe: pd.DataFrame, boolean_columns: list[str], transformation_log: TransformationLog
) -> pd.DataFrame:
    cleaned = dataframe.copy()
    for column in boolean_columns:
        cleaned[column] = cleaned[column].map(BOOLEAN_LABELS).astype("category")
        transformation_log.record(
            "dtype_correction", column, "converted_to_boolean_category", labels=BOOLEAN_LABELS
        )
    return cleaned


def convert_identifier_columns(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    cleaned = dataframe.copy()
    for column in IDENTIFIER_VARIABLES:
        if column not in cleaned.columns:
            continue
        cleaned[column] = cleaned[column].astype("Int64")
        transformation_log.record("dtype_correction", column, "converted_to_nullable_int64")
    return cleaned


def convert_numeric_role_dtypes(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    """Whole-number continuous/conditional variables become nullable Int64;
    decimal measurements (e.g. TEMPF after unit correction) stay float64."""
    cleaned = dataframe.copy()
    for column in CONTINUOUS_NUMERICAL_VARIABLES | CONDITIONAL_NUMERICAL_VARIABLES:
        if column not in cleaned.columns:
            continue
        if _is_whole_number_column(cleaned[column]):
            cleaned[column] = cleaned[column].astype("Int64")
            transformation_log.record("dtype_correction", column, "converted_to_nullable_int64")
    return cleaned


def _format_numeric_label(value):
    """Formats a numeric code as a clean string label ("1" not "1.0"), so
    every category dtype in the cleaned dataset is string-typed. This
    matters beyond cosmetics: a later step fills missing categories with
    the string "Missing", and pyarrow (used to save the cleaned dataset
    as parquet) cannot represent a category dtype whose categories mix
    numeric and string types."""
    if pd.isna(value):
        return pd.NA
    return str(int(value)) if float(value).is_integer() else str(value)


def convert_nominal_code_columns(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    """RFV-style nominal codes become category dtype with clean integer-
    looking labels, so they are handled like any other categorical
    variable during imputation rather than as a continuous measurement."""
    cleaned = dataframe.copy()

    for column in NOMINAL_CODE_VARIABLES:
        if column not in cleaned.columns:
            continue
        cleaned[column] = cleaned[column].map(_format_numeric_label).astype("category")
        transformation_log.record("dtype_correction", column, "converted_to_nominal_category")

    return cleaned


def convert_generic_categorical_columns(
    dataframe: pd.DataFrame, categorical_columns: list[str], transformation_log: TransformationLog
) -> pd.DataFrame:
    """Casts remaining generic categorical columns to pandas "category"
    dtype. Numeric columns are formatted as clean string labels ("1" not
    "1.0") so every category in the cleaned dataset is string-typed."""
    cleaned = dataframe.copy()

    for column in categorical_columns:
        series = cleaned[column]
        if pd.api.types.is_numeric_dtype(series):
            series = series.map(_format_numeric_label)

        cleaned[column] = series.astype("category")
        transformation_log.record("dtype_correction", column, "converted_to_category")

    return cleaned
