"""Removes columns with zero informational value (a single distinct value
across every row). Survey, identifier, and target-source variables are
exempt: a constant survey/identifier column is still structurally
meaningful and must be preserved regardless of variance, and the
target-source columns (ADMITHOS/OBSHOS) must always survive cleaning even
if they happen to be locally constant in a particular sample, since
target derivation depends on them unconditionally."""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.variable_roles import IDENTIFIER_VARIABLES, SURVEY_VARIABLES, TARGET_SOURCE_VARIABLES

EXEMPT_FROM_CONSTANT_REMOVAL = SURVEY_VARIABLES | IDENTIFIER_VARIABLES | TARGET_SOURCE_VARIABLES


def remove_constant_columns(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    columns_to_drop = []

    for column in dataframe.columns:
        if column in EXEMPT_FROM_CONSTANT_REMOVAL:
            continue
        if dataframe[column].nunique(dropna=True) <= 1:
            columns_to_drop.append(column)

    if columns_to_drop:
        transformation_log.record(
            "remove_constant_columns",
            "*",
            "dropped_constant_columns",
            count=len(columns_to_drop),
            columns=columns_to_drop,
        )

    return dataframe.drop(columns=columns_to_drop)
