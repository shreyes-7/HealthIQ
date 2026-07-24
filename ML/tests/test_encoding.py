"""Unit tests for CategoricalEncoder (ML/feature_engineering/encoding.py)."""

import pandas as pd

from ML.feature_engineering.encoding import CategoricalEncoder


def test_one_hot_drops_reference_category():
    dataframe = pd.DataFrame({"SEX": pd.Categorical(["1", "2", "1", "1"])})
    encoder = CategoricalEncoder(one_hot_max_categories=15).fit(dataframe, ["SEX"])
    encoded = encoder.transform(dataframe)

    # "1" is the majority category and should be dropped as the reference.
    assert "SEX__1" not in encoded.columns
    assert "SEX__2" in encoded.columns
    assert encoded["SEX__2"].tolist() == [0, 1, 0, 0]


def test_frequency_encoding_for_high_cardinality():
    dataframe = pd.DataFrame({"DIAG1": pd.Categorical(["A", "A", "B", "C"])})
    encoder = CategoricalEncoder(one_hot_max_categories=1).fit(dataframe, ["DIAG1"])
    encoded = encoder.transform(dataframe)

    assert "DIAG1__frequency" in encoded.columns
    assert encoded["DIAG1__frequency"].iloc[0] == 0.5  # "A" appears 2/4 times
    assert encoded["DIAG1__frequency"].iloc[2] == 0.25  # "B" appears 1/4 times


def test_unseen_category_at_transform_time_does_not_crash():
    train = pd.DataFrame({"DIAG1": pd.Categorical(["A", "A", "B"])})
    unseen = pd.DataFrame({"DIAG1": pd.Categorical(["Z"])})

    encoder = CategoricalEncoder(one_hot_max_categories=1).fit(train, ["DIAG1"])
    encoded = encoder.transform(unseen)

    # An unseen category falls back to the minimum observed frequency rather than raising.
    assert not encoded["DIAG1__frequency"].isna().any()


def test_feature_metadata_records_reference_category():
    dataframe = pd.DataFrame({"SEX": pd.Categorical(["1", "2", "1"])})
    encoder = CategoricalEncoder(one_hot_max_categories=15).fit(dataframe, ["SEX"])
    metadata = encoder.get_feature_metadata()

    assert metadata["SEX"]["encoding"] == "one_hot"
    assert metadata["SEX"]["reference_category"] == "1"
