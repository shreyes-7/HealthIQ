"""Unit tests for leakage exclusion (ML/feature_engineering/leakage_exclusion.py).

This is the most consequence-heavy list in the whole pipeline: missing a
column here means the model could trivially learn the answer from a
feature that is only known after the admission decision. These tests
pin down the specific columns discovered during Milestone 4/6's
documentation review so a future edit can't silently drop one.
"""

from ML.feature_engineering.leakage_exclusion import get_excluded_leakage_columns


def test_disposition_and_target_source_columns_are_excluded():
    excluded = get_excluded_leakage_columns()
    for column in ("ADMITHOS", "OBSHOS", "LWBS", "DIEDED", "TRANPSYC"):
        assert column in excluded, f"{column} must be excluded (VISIT DISPOSITION block)"


def test_post_admission_hospital_course_columns_are_excluded():
    excluded = get_excluded_leakage_columns()
    for column in ("LOS", "ADMIT", "ADMTPHYS", "BOARDED", "HDSTAT", "HDDIAG1"):
        assert column in excluded, f"{column} must be excluded (post-admission hospital course)"


def test_facility_level_questionnaire_columns_are_excluded():
    excluded = get_excluded_leakage_columns()
    for column in ("AMBDIV", "BEDCZAR", "HLIST", "EMEDRES"):
        assert column in excluded, f"{column} must be excluded (facility-level questionnaire)"


def test_legitimate_predictors_are_not_excluded():
    excluded = get_excluded_leakage_columns()
    for column in ("AGE", "SEX", "PULSE", "BPSYS", "CONSULT", "TOTDIAG", "DIAG1", "IMMEDR"):
        assert column not in excluded, f"{column} is a legitimate pre-decision predictor and must not be excluded"
