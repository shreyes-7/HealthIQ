"""Unit tests for target derivation (ML/feature_engineering/target.py).

Mirrors Milestone 1's documented definition: hospital_admission = 1 if
ADMITHOS == "Yes" or OBSHOS == "Yes" (post-cleaning category values).
"""

import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME, derive_target


def test_admitted_directly_is_positive():
    dataframe = pd.DataFrame({"ADMITHOS": ["Yes"], "OBSHOS": ["No"]})
    target = derive_target(dataframe)
    assert target.iloc[0] == 1


def test_admitted_via_observation_is_positive():
    dataframe = pd.DataFrame({"ADMITHOS": ["No"], "OBSHOS": ["Yes"]})
    target = derive_target(dataframe)
    assert target.iloc[0] == 1


def test_not_admitted_either_way_is_negative():
    dataframe = pd.DataFrame({"ADMITHOS": ["No"], "OBSHOS": ["No"]})
    target = derive_target(dataframe)
    assert target.iloc[0] == 0


def test_target_column_is_named_hospital_admission():
    dataframe = pd.DataFrame({"ADMITHOS": ["No"], "OBSHOS": ["No"]})
    target = derive_target(dataframe)
    assert target.name == TARGET_COLUMN_NAME == "hospital_admission"
