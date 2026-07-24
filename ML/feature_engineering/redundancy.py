"""Removes redundant and near-zero-variance variables before encoding.

Two distinct kinds of redundancy are handled:

1. Near-duplicate variables: Milestone 2's EDA found RFV1-5 correlate at
   1.0 with RFV13D-53D (their 3-digit truncated recode). Encoding both
   would duplicate the same information. The detailed 5-digit RFV1-5
   codes are dropped in favor of the coarser 3-digit recodes: several
   hundred fewer categories per variable, which keeps one-hot encoding
   tractable and more interpretable while losing only fine-grained detail
   within an already-narrow classification code.

2. Near-zero-variance categorical columns: many per-medication-slot
   fields (RX16CAT4, DRUGID30, etc.) have a dominant category covering
   99%+ of visits (most patients are on 0-3 medications, so slots 16-30
   are "not applicable" for nearly everyone). One-hot encoding all ~365
   such columns would add ~400+ near-empty feature columns with almost no
   discriminative signal. This is a conservative filter (99% threshold)
   deliberately deferred from Milestone 3 to here, where the alternative
   (encoding) makes the cost of not filtering concrete. A more rigorous,
   target-aware feature selection (mutual information, tree importance,
   RFE) remains Milestone 6's job.
"""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog

REDUNDANT_DETAILED_RFV_CODES = {"RFV1", "RFV2", "RFV3", "RFV4", "RFV5"}
NEAR_ZERO_VARIANCE_THRESHOLD = 0.99


def remove_redundant_rfv_codes(dataframe: pd.DataFrame, transformation_log: TransformationLog) -> pd.DataFrame:
    columns_to_drop = [column for column in REDUNDANT_DETAILED_RFV_CODES if column in dataframe.columns]
    if columns_to_drop:
        transformation_log.record(
            "remove_redundant_variables",
            "*",
            "dropped_near_duplicate_rfv_codes",
            columns=columns_to_drop,
            reason="correlation 1.0 with RFV*3D 3-digit recode (Milestone 2 EDA); kept the coarser recode "
            "for tractable, interpretable one-hot encoding",
        )
    return dataframe.drop(columns=columns_to_drop)


def remove_near_zero_variance_categorical(
    dataframe: pd.DataFrame,
    categorical_columns: list[str],
    transformation_log: TransformationLog,
    threshold: float = NEAR_ZERO_VARIANCE_THRESHOLD,
) -> pd.DataFrame:
    columns_to_drop = []
    for column in categorical_columns:
        if column not in dataframe.columns:
            continue
        dominant_frequency = dataframe[column].value_counts(normalize=True, dropna=False).iloc[0]
        if dominant_frequency >= threshold:
            columns_to_drop.append(column)

    if columns_to_drop:
        transformation_log.record(
            "remove_redundant_variables",
            "*",
            "dropped_near_zero_variance_columns",
            count=len(columns_to_drop),
            threshold=threshold,
            columns=columns_to_drop,
        )

    return dataframe.drop(columns=columns_to_drop)
