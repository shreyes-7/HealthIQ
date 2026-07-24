"""Fills missing values using per-role strategies.

- Continuous numerical variables: median imputation (robust to skew).
- Categorical variables (including boolean-turned-category and nominal
  RFV codes, since both are cast to category dtype by dtype_correction):
  filled with an explicit "Missing" category rather than the mode, so
  unknown/blank/not-applicable remains visible to downstream models
  instead of being silently folded into the majority class.
- Conditional numerical variables (LOS, OBSSTAY, AGEDAYS, BOARDED) are
  deliberately NOT imputed: the value does not conceptually exist for
  most rows (e.g. LOS for a non-admitted visit), and filling it would
  fabricate information rather than clean it. This is documented, not
  silently skipped.
- Survey and identifier variables are never touched (excluded by dtype:
  they are never cast to category, and are not in the continuous set).
"""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.variable_roles import CONDITIONAL_NUMERICAL_VARIABLES, CONTINUOUS_NUMERICAL_VARIABLES

MISSING_CATEGORY_LABEL = "Missing"


def fit_continuous_medians(dataframe: pd.DataFrame) -> dict:
    """Learns the per-column median to impute with. Kept separate from
    applying it so a pipeline can fit these medians once (on a training
    split) and reapply the SAME values to any future dataset, rather than
    recomputing a different median from whatever data happens to be
    passed at transform time.

    For integer-typed columns (whole-number vitals/counts already
    converted to nullable Int64 by dtype_correction), the median is
    rounded to the nearest whole number. With an even count of non-null
    values the raw median can land on a .5 boundary (e.g. 73.5) even
    though every underlying value is a whole number -- both because a
    fractional heart rate/count isn't a real recorded value, and because
    pandas' nullable Int64 dtype cannot hold a fractional fillna value at
    all (raises TypeError).
    """
    medians = {}
    for column in CONTINUOUS_NUMERICAL_VARIABLES:
        if column not in dataframe.columns:
            continue

        median_value = dataframe[column].median()
        if pd.api.types.is_integer_dtype(dataframe[column]):
            median_value = round(median_value)
        medians[column] = float(median_value)

    return medians


def apply_continuous_imputation(
    dataframe: pd.DataFrame, medians: dict, transformation_log: TransformationLog
) -> pd.DataFrame:
    cleaned = dataframe.copy()

    for column, median_value in medians.items():
        if column not in cleaned.columns:
            continue

        missing_count = int(cleaned[column].isna().sum())
        if missing_count == 0:
            continue

        cleaned[column] = cleaned[column].fillna(median_value)
        transformation_log.record(
            "impute_missing_values",
            column,
            "median_imputed",
            count=missing_count,
            median_value=median_value,
        )

    return cleaned


def impute_continuous_numerical(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    """Convenience one-shot helper (fit + apply on the same data). Used
    when there is no separate training split to fit on yet."""
    medians = fit_continuous_medians(dataframe)
    return apply_continuous_imputation(dataframe, medians, transformation_log)


def document_conditional_numerical_skip(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> None:
    """Records the NaN count for conditional variables without filling
    them, so the decision not to impute is visible in the audit trail."""
    for column in CONDITIONAL_NUMERICAL_VARIABLES:
        if column not in dataframe.columns:
            continue

        missing_count = int(dataframe[column].isna().sum())
        transformation_log.record(
            "impute_missing_values",
            column,
            "left_as_nan_conditionally_not_applicable",
            count=missing_count,
            reason="value is only defined for a subset of visits (codebook sentinel -7 = Not applicable)",
        )


def impute_categorical_columns(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    cleaned = dataframe.copy()

    for column in cleaned.columns:
        series = cleaned[column]
        if not isinstance(series.dtype, pd.CategoricalDtype):
            continue

        missing_count = int(series.isna().sum())
        if missing_count == 0:
            continue

        if MISSING_CATEGORY_LABEL not in series.cat.categories:
            series = series.cat.add_categories([MISSING_CATEGORY_LABEL])

        cleaned[column] = series.fillna(MISSING_CATEGORY_LABEL)
        transformation_log.record(
            "impute_missing_values", column, "filled_with_missing_category", count=missing_count
        )

    return cleaned
