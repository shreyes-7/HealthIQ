"""Derives the prediction target from the cleaned dataset.

Matches the definition documented in Milestone 1
(ML/reports/target_and_survey_variables.md): hospital_admission = 1 if
ADMITHOS == "Yes" or OBSHOS == "Yes", else 0. After Milestone 3 cleaning,
these are "No"/"Yes" category columns rather than raw 0/1 floats.
"""

import pandas as pd

from ML.cleaning.variable_roles import TARGET_SOURCE_VARIABLES

TARGET_COLUMN_NAME = "hospital_admission"
ADMITTED_TO_HOSPITAL_FLAG = "ADMITHOS"
ADMITTED_VIA_OBSERVATION_FLAG = "OBSHOS"

# Kept in sync with ML.cleaning.variable_roles.TARGET_SOURCE_VARIABLES,
# which exempts these columns from constant-column removal during
# cleaning -- if this assertion ever fires, that exemption has drifted
# out of sync with what target derivation actually reads.
assert {ADMITTED_TO_HOSPITAL_FLAG, ADMITTED_VIA_OBSERVATION_FLAG} == TARGET_SOURCE_VARIABLES


def derive_target(dataframe: pd.DataFrame) -> pd.Series:
    is_admitted = (
        (dataframe[ADMITTED_TO_HOSPITAL_FLAG] == "Yes") | (dataframe[ADMITTED_VIA_OBSERVATION_FLAG] == "Yes")
    )
    return is_admitted.astype(int).rename(TARGET_COLUMN_NAME)
