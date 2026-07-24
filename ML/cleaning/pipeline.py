"""Orchestrates the Milestone 3 cleaning pipeline in a fixed order, with a
fit/transform contract so the same cleaning decisions learned from one
dataset (e.g. a training split) can be reapplied identically to another
(e.g. a test split, or a future inference request).

Order matters: sentinel/annotation codes must become NaN before unit
correction (so real values aren't divided incorrectly) and before dtype
correction and imputation (so "missingness" reflects final values, not
raw sentinel codes). Text standardization runs on the original string
columns before they are cast to category dtype, since categories become
fixed once a column is categorical.

Most steps are stateless rules (sentinel codes, implied-decimal
correction, text standardization) and are safe to simply rerun on any new
data. Four decisions are genuinely LEARNED from the data and must be
reused rather than recomputed at transform time, or a test/inference
dataset could silently end up with a different column set or different
imputed values than the training data: which columns were exact
duplicates, which were constant, which were treated as boolean, and what
median to impute with. These are captured in the `fitted_state` dict
returned by fit_clean_dataset() and consumed by transform_clean_dataset().

Survey design variables and identifier variables are excluded from every
step except duplicate-row removal: they are never sentinel-converted,
never imputed, and never dtype-corrected beyond identifiers becoming a
clean nullable-integer type.
"""

import pandas as pd

from ML.cleaning.constant_columns import remove_constant_columns
from ML.cleaning.duplicates import remove_duplicate_columns, remove_duplicate_rows
from ML.cleaning.dtype_correction import (
    convert_boolean_columns,
    convert_generic_categorical_columns,
    convert_identifier_columns,
    convert_nominal_code_columns,
    convert_numeric_role_dtypes,
    detect_boolean_columns,
)
from ML.cleaning.imputation import (
    apply_continuous_imputation,
    document_conditional_numerical_skip,
    fit_continuous_medians,
    impute_categorical_columns,
)
from ML.cleaning.sentinel import convert_non_numeric_annotations_to_nan, convert_sentinels_to_nan
from ML.cleaning.standardize_text import standardize_string_columns
from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.unit_correction import apply_implied_decimal_correction
from ML.cleaning.variable_roles import get_all_special_role_columns


def fit_clean_dataset(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, TransformationLog, dict]:
    """Cleans `dataframe` and learns the reusable cleaning state (dropped
    columns, boolean-column list, imputation medians) from it."""
    log = TransformationLog()

    original_string_columns = [
        column for column in dataframe.columns if pd.api.types.is_string_dtype(dataframe[column])
    ]

    cleaned = remove_duplicate_rows(dataframe, log)
    cleaned = convert_sentinels_to_nan(cleaned, log)
    cleaned = convert_non_numeric_annotations_to_nan(cleaned, log)
    cleaned = apply_implied_decimal_correction(cleaned, log)

    cleaned = remove_duplicate_columns(cleaned, log)
    duplicate_columns_dropped = [entry["column"] for entry in log.entries_for_step("remove_duplicate_columns")]

    cleaned = remove_constant_columns(cleaned, log)
    constant_column_entry = next(iter(log.entries_for_step("remove_constant_columns")), None)
    constant_columns_dropped = constant_column_entry["columns"] if constant_column_entry else []

    remaining_string_columns = [column for column in original_string_columns if column in cleaned.columns]
    cleaned = standardize_string_columns(cleaned, remaining_string_columns, log)

    special_role_columns = get_all_special_role_columns()
    boolean_columns = detect_boolean_columns(cleaned)
    categorical_columns = [
        column for column in cleaned.columns if column not in special_role_columns and column not in boolean_columns
    ]

    cleaned = convert_boolean_columns(cleaned, boolean_columns, log)
    cleaned = convert_identifier_columns(cleaned, log)
    cleaned = convert_numeric_role_dtypes(cleaned, log)
    cleaned = convert_nominal_code_columns(cleaned, log)
    cleaned = convert_generic_categorical_columns(cleaned, categorical_columns, log)

    continuous_medians = fit_continuous_medians(cleaned)
    cleaned = apply_continuous_imputation(cleaned, continuous_medians, log)
    document_conditional_numerical_skip(cleaned, log)
    cleaned = impute_categorical_columns(cleaned, log)

    fitted_state = {
        "original_string_columns": original_string_columns,
        "duplicate_columns_dropped": duplicate_columns_dropped,
        "constant_columns_dropped": constant_columns_dropped,
        "boolean_columns": boolean_columns,
        "categorical_columns": categorical_columns,
        "continuous_medians": continuous_medians,
    }
    return cleaned, log, fitted_state


def transform_clean_dataset(dataframe: pd.DataFrame, fitted_state: dict) -> tuple[pd.DataFrame, TransformationLog]:
    """Applies the SAME cleaning decisions learned by fit_clean_dataset()
    to a new dataset, instead of re-detecting them from this data."""
    log = TransformationLog()

    cleaned = remove_duplicate_rows(dataframe, log)
    cleaned = convert_sentinels_to_nan(cleaned, log)
    cleaned = convert_non_numeric_annotations_to_nan(cleaned, log)
    cleaned = apply_implied_decimal_correction(cleaned, log)

    columns_to_drop = [
        column
        for column in fitted_state["duplicate_columns_dropped"] + fitted_state["constant_columns_dropped"]
        if column in cleaned.columns
    ]
    cleaned = cleaned.drop(columns=columns_to_drop)
    log.record(
        "reuse_fitted_column_drops", "*", "dropped_columns_identified_during_fit", columns=columns_to_drop
    )

    remaining_string_columns = [
        column for column in fitted_state["original_string_columns"] if column in cleaned.columns
    ]
    cleaned = standardize_string_columns(cleaned, remaining_string_columns, log)

    cleaned = convert_boolean_columns(cleaned, fitted_state["boolean_columns"], log)
    cleaned = convert_identifier_columns(cleaned, log)
    cleaned = convert_numeric_role_dtypes(cleaned, log)
    cleaned = convert_nominal_code_columns(cleaned, log)
    cleaned = convert_generic_categorical_columns(cleaned, fitted_state["categorical_columns"], log)

    cleaned = apply_continuous_imputation(cleaned, fitted_state["continuous_medians"], log)
    document_conditional_numerical_skip(cleaned, log)
    cleaned = impute_categorical_columns(cleaned, log)

    return cleaned, log
