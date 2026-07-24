"""Unit tests for derived clinical features (ML/feature_engineering/derived_features.py)."""

import pandas as pd

from ML.feature_engineering.derived_features import add_derived_clinical_features


def _base_dataframe(**overrides) -> pd.DataFrame:
    row = {"PULSE": 80, "BPSYS": 120, "BPDIAS": 80, "TEMPF": 98.6, "AGE": 30}
    row.update(overrides)
    return pd.DataFrame([row])


def test_shock_index_is_pulse_over_systolic_bp():
    enriched = add_derived_clinical_features(_base_dataframe(PULSE=90, BPSYS=120))
    assert abs(enriched["SHOCK_INDEX"].iloc[0] - 0.75) < 1e-9


def test_shock_index_guards_against_division_by_zero():
    # BPSYS == 0 is a rare but documented valid NHAMCS code, not a sentinel.
    enriched = add_derived_clinical_features(_base_dataframe(BPSYS=0, PULSE=80))
    assert enriched["SHOCK_INDEX"].notna().all()
    assert not enriched["SHOCK_INDEX"].isin([float("inf"), float("-inf")]).any()


def test_pulse_pressure_is_systolic_minus_diastolic():
    enriched = add_derived_clinical_features(_base_dataframe(BPSYS=120, BPDIAS=80))
    assert enriched["PULSE_PRESSURE"].iloc[0] == 40


def test_fever_flag_threshold():
    below = add_derived_clinical_features(_base_dataframe(TEMPF=99.0))
    at_or_above = add_derived_clinical_features(_base_dataframe(TEMPF=100.4))
    assert below["FEVER_FLAG"].iloc[0] == "No"
    assert at_or_above["FEVER_FLAG"].iloc[0] == "Yes"


def test_age_group_buckets():
    infant = add_derived_clinical_features(_base_dataframe(AGE=0))
    adult = add_derived_clinical_features(_base_dataframe(AGE=30))
    older_adult = add_derived_clinical_features(_base_dataframe(AGE=70))

    assert infant["AGE_GROUP"].iloc[0] == "infant_0_1"
    assert adult["AGE_GROUP"].iloc[0] == "adult_18_64"
    assert older_adult["AGE_GROUP"].iloc[0] == "older_adult_65_plus"
