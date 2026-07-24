"""Unit tests for continuous-variable imputation (ML/cleaning/imputation.py).

Includes a regression test for a real bug found during Milestone 11
validation: on an even-count sample, the median of a whole-number vital
can land on a .5 boundary (e.g. 73.5), which pandas' nullable Int64 dtype
cannot hold via fillna -- it raised TypeError. Discovered by the
pipeline-reproducibility check in ML/scripts/run_validation.py on a
500-row sample; fixed by rounding integer-typed columns' medians.
"""

import pandas as pd

from ML.cleaning.imputation import apply_continuous_imputation, fit_continuous_medians
from ML.cleaning.transformation_log import TransformationLog


def test_median_of_even_count_int64_column_is_rounded():
    # Non-null values [70, 77] -> raw median 73.5, which must be rounded
    # for an Int64 column (not left fractional).
    dataframe = pd.DataFrame({"PULSE": pd.array([70, 77, None], dtype="Int64")})
    medians = fit_continuous_medians(dataframe)

    assert medians["PULSE"] == float(round(73.5))


def test_apply_continuous_imputation_does_not_raise_on_int64_column():
    dataframe = pd.DataFrame({"PULSE": pd.array([70, 77, None], dtype="Int64")})
    medians = fit_continuous_medians(dataframe)

    # This is the exact call that raised TypeError before the fix.
    imputed = apply_continuous_imputation(dataframe, medians, TransformationLog())

    assert imputed["PULSE"].isna().sum() == 0
    assert imputed["PULSE"].dtype == "Int64"


def test_float_column_median_is_not_rounded():
    dataframe = pd.DataFrame({"TEMPF": [98.0, 99.3, None]})
    medians = fit_continuous_medians(dataframe)

    assert medians["TEMPF"] == 98.65


def test_imputation_is_logged_with_correct_count():
    dataframe = pd.DataFrame({"AGE": [10.0, 20.0, None, None]})
    medians = fit_continuous_medians(dataframe)
    log = TransformationLog()
    apply_continuous_imputation(dataframe, medians, log)

    entries = log.entries_for_step("impute_missing_values")
    assert entries[0]["column"] == "AGE"
    assert entries[0]["count"] == 2
