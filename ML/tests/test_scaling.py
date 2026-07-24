"""Unit tests for NumericalScaler (ML/feature_engineering/scaling.py)."""

import pandas as pd

from ML.feature_engineering.scaling import NumericalScaler


def test_fit_transform_produces_zero_mean_unit_std():
    dataframe = pd.DataFrame({"AGE": [10, 20, 30, 40, 50]})
    scaler = NumericalScaler().fit(dataframe, ["AGE"])
    scaled = scaler.transform(dataframe)

    assert abs(scaled["AGE"].mean()) < 1e-9
    assert abs(scaled["AGE"].std(ddof=0) - 1.0) < 1e-9


def test_transform_reuses_fitted_statistics_not_new_data_statistics():
    train = pd.DataFrame({"AGE": [10, 20, 30, 40, 50]})  # mean=30
    other = pd.DataFrame({"AGE": [1000, 1000, 1000]})  # very different distribution

    scaler = NumericalScaler().fit(train, ["AGE"])
    scaled_other = scaler.transform(other)

    # Using the TRAIN mean (30) and std, not re-fit on `other`'s own mean/std.
    expected = (1000 - 30) / train["AGE"].std(ddof=0)
    assert abs(scaled_other["AGE"].iloc[0] - expected) < 1e-6


def test_feature_metadata_allows_inverse_transform():
    dataframe = pd.DataFrame({"AGE": [10, 20, 30, 40, 50]})
    scaler = NumericalScaler().fit(dataframe, ["AGE"])
    metadata = scaler.get_feature_metadata()

    assert metadata["AGE"]["mean"] == 30.0
    assert metadata["AGE"]["std"] > 0
