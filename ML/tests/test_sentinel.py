"""Unit tests for NHAMCS sentinel-code handling (ML/cleaning/sentinel.py)."""

import numpy as np
import pandas as pd

from ML.cleaning.sentinel import convert_non_numeric_annotations_to_nan, convert_sentinels_to_nan
from ML.cleaning.transformation_log import TransformationLog


def test_numeric_sentinel_codes_become_nan():
    dataframe = pd.DataFrame({"AGE": [25.0, -7.0, -8.0, -9.0, 40.0], "PATWT": [100.0] * 5})
    cleaned = convert_sentinels_to_nan(dataframe, TransformationLog())

    assert cleaned["AGE"].tolist()[:1] == [25.0]
    assert cleaned["AGE"].iloc[4] == 40.0
    assert cleaned["AGE"].iloc[1:4].isna().all()


def test_string_sentinel_codes_become_nan():
    dataframe = pd.Series(["-9", "T833", "-7", "K297"], name="DIAG1", dtype="str").to_frame()
    dataframe["PATWT"] = 100.0
    cleaned = convert_sentinels_to_nan(dataframe, TransformationLog())

    assert cleaned["DIAG1"].iloc[0] is None or pd.isna(cleaned["DIAG1"].iloc[0])
    assert cleaned["DIAG1"].iloc[1] == "T833"
    assert cleaned["DIAG1"].iloc[2] is None or pd.isna(cleaned["DIAG1"].iloc[2])
    assert cleaned["DIAG1"].iloc[3] == "K297"


def test_survey_and_identifier_columns_are_never_touched():
    # -7 would be converted to NaN in any ordinary column; PATWT/HOSPCODE must be exempt.
    dataframe = pd.DataFrame({"PATWT": [-7.0, 100.0], "HOSPCODE": [-7.0, 5.0], "AGE": [-7.0, 30.0]})
    cleaned = convert_sentinels_to_nan(dataframe, TransformationLog())

    assert cleaned["PATWT"].iloc[0] == -7.0
    assert cleaned["HOSPCODE"].iloc[0] == -7.0
    assert pd.isna(cleaned["AGE"].iloc[0])


def test_sentinel_conversion_is_logged():
    dataframe = pd.DataFrame({"AGE": [-7.0, 30.0], "PATWT": [100.0, 100.0]})
    log = TransformationLog()
    convert_sentinels_to_nan(dataframe, log)

    entries = log.entries_for_step("sentinel_to_nan")
    assert len(entries) == 1
    assert entries[0]["column"] == "AGE"
    assert entries[0]["count"] == 1


def test_doppler_annotation_code_becomes_nan_not_literal_value():
    # PULSE == 998 means "measured by Doppler", not a literal heart rate of 998.
    dataframe = pd.DataFrame({"PULSE": [80.0, 998.0, 72.0]})
    cleaned = convert_non_numeric_annotations_to_nan(dataframe, TransformationLog())

    assert cleaned["PULSE"].iloc[0] == 80.0
    assert pd.isna(cleaned["PULSE"].iloc[1])
    assert cleaned["PULSE"].iloc[2] == 72.0
