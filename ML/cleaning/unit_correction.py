"""Corrects codebook-documented implied-decimal encodings.

TEMPF/TEMPDF: "There is an implied decimal between the third and fourth
digits" (e.g. raw 986 means 98.6 Fahrenheit).

RFV1-5: "10050-89990 = 1005.0-8999.0" (Reason for Visit classification
codes are stored as the real code x 10).

Run this AFTER sentinel conversion so NaN values are not divided.
"""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.variable_roles import IMPLIED_DECIMAL_VARIABLES


def apply_implied_decimal_correction(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    cleaned = dataframe.copy()

    for column in IMPLIED_DECIMAL_VARIABLES:
        if column not in cleaned.columns:
            continue

        affected_count = int(cleaned[column].notna().sum())
        if affected_count == 0:
            continue

        cleaned[column] = cleaned[column] / 10.0
        transformation_log.record(
            "implied_decimal_correction",
            column,
            "divided_by_10",
            count=affected_count,
            reason="codebook documents an implied decimal for this variable",
        )

    return cleaned
