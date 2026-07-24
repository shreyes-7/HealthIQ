"""Converts NHAMCS sentinel/missing codes to proper NaN.

Applies to every column except survey design variables (preserved
untouched) and identifier variables (always fully populated, not
measurements). Handles both numeric sentinels (-7.0/-8.0/-9.0) and their
string equivalents ("-7"/"-8"/"-9"), since NHAMCS uses the same convention
for both numeric and text-coded fields (confirmed in Milestone 1/3
investigation: no other negative codes and no blank strings appear
anywhere in the dataset).

Also converts codebook-documented non-numeric annotation codes (e.g.
PULSE == 998 meaning "measured by Doppler", not a literal heart rate) to
NaN.
"""

import numpy as np
import pandas as pd

from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.variable_roles import (
    IDENTIFIER_VARIABLES,
    NON_NUMERIC_ANNOTATION_CODES,
    SENTINEL_CODES,
    SURVEY_VARIABLES,
)

SENTINEL_STRINGS = {str(code) for code in SENTINEL_CODES}
EXCLUDED_FROM_SENTINEL_CONVERSION = SURVEY_VARIABLES | IDENTIFIER_VARIABLES


def convert_sentinels_to_nan(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    cleaned = dataframe.copy()

    for column in cleaned.columns:
        if column in EXCLUDED_FROM_SENTINEL_CONVERSION:
            continue

        series = cleaned[column]
        if pd.api.types.is_numeric_dtype(series):
            is_sentinel = series.isin(SENTINEL_CODES)
        else:
            is_sentinel = series.astype("string").str.strip().isin(SENTINEL_STRINGS)

        sentinel_count = int(is_sentinel.sum())
        if sentinel_count > 0:
            cleaned.loc[is_sentinel, column] = np.nan
            transformation_log.record(
                "sentinel_to_nan",
                column,
                "converted_sentinel_codes_to_nan",
                count=sentinel_count,
            )

    return cleaned


def convert_non_numeric_annotations_to_nan(
    dataframe: pd.DataFrame, transformation_log: TransformationLog
) -> pd.DataFrame:
    cleaned = dataframe.copy()

    for column, codes in NON_NUMERIC_ANNOTATION_CODES.items():
        if column not in cleaned.columns:
            continue

        is_annotation = cleaned[column].isin(codes)
        annotation_count = int(is_annotation.sum())
        if annotation_count > 0:
            cleaned.loc[is_annotation, column] = np.nan
            transformation_log.record(
                "non_numeric_annotation_to_nan",
                column,
                "converted_annotation_codes_to_nan",
                count=annotation_count,
                codes=sorted(codes),
            )

    return cleaned
