"""Removes exact duplicate rows and exact duplicate columns."""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.variable_roles import IDENTIFIER_VARIABLES, SURVEY_VARIABLES, TARGET_SOURCE_VARIABLES

# Survey, identifier, and target-source columns must never be dropped as
# a "duplicate" of some other column, even if their values happen to
# coincide within a particular sample (e.g. OBSHOS is positive in only
# ~1% of visits, so within a small sample it can be all-zero and
# therefore identical to several other rare, unrelated flag columns).
EXEMPT_FROM_DUPLICATE_COLUMN_REMOVAL = SURVEY_VARIABLES | IDENTIFIER_VARIABLES | TARGET_SOURCE_VARIABLES


def remove_duplicate_rows(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    is_duplicate = dataframe.duplicated(keep="first")
    duplicate_count = int(is_duplicate.sum())

    cleaned = dataframe.loc[~is_duplicate].reset_index(drop=True)
    transformation_log.record(
        "remove_duplicate_rows", "*", "dropped_duplicate_rows", count=duplicate_count
    )
    return cleaned


def remove_duplicate_columns(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    """Detect columns with identical content using a hash pre-filter, then
    verify with an exact equality check before dropping (hash collisions
    are rare but must not silently drop a non-duplicate column). Exempt
    columns are never dropped, even as the "duplicate" side of a pair."""
    column_hashes = {}
    for column in dataframe.columns:
        column_hashes.setdefault(
            tuple(pd.util.hash_pandas_object(dataframe[column], index=False)), []
        ).append(column)

    columns_to_drop = []
    for candidate_columns in column_hashes.values():
        if len(candidate_columns) < 2:
            continue

        # Prefer an exempt column as the kept reference so a protected
        # column is never the one removed; among droppable columns, keep
        # the first and drop the rest.
        droppable = [c for c in candidate_columns if c not in EXEMPT_FROM_DUPLICATE_COLUMN_REMOVAL]
        exempt_present = [c for c in candidate_columns if c in EXEMPT_FROM_DUPLICATE_COLUMN_REMOVAL]
        reference_column = exempt_present[0] if exempt_present else droppable[0]
        columns_to_check_against_reference = [c for c in candidate_columns if c != reference_column]

        for other_column in columns_to_check_against_reference:
            if other_column in EXEMPT_FROM_DUPLICATE_COLUMN_REMOVAL:
                continue
            if dataframe[reference_column].equals(dataframe[other_column]):
                columns_to_drop.append(other_column)
                transformation_log.record(
                    "remove_duplicate_columns",
                    other_column,
                    "dropped_duplicate_column",
                    duplicate_of=reference_column,
                )

    return dataframe.drop(columns=columns_to_drop)
