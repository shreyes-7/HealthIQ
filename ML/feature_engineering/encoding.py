"""Encodes categorical variables using a tiered strategy that balances
interpretability against dimensionality:

- Low-cardinality columns (<= ONE_HOT_MAX_CATEGORIES distinct values):
  one-hot encoded, dropping the most frequent category per column as the
  reference (avoids the dummy-variable trap; each remaining dummy column
  is directly interpretable, e.g. "SEX__2" = 1 means "this patient's SEX
  code is 2").
- High-cardinality columns (diagnosis codes, drug codes, arrival time):
  frequency-encoded (replaced by how often that category occurred in the
  fitted data) instead of one-hot, which would otherwise add thousands of
  near-empty dummy columns. This still produces a single, interpretable
  numeric feature ("how common is this code").

Follows a scikit-learn-style fit/transform contract so it can be refit on
a training split only, once Milestone 7 (Train/Test Split) exists,
without changing this code.
"""

import pandas as pd

ONE_HOT_MAX_CATEGORIES = 15


class CategoricalEncoder:
    def __init__(self, one_hot_max_categories: int = ONE_HOT_MAX_CATEGORIES):
        self.one_hot_max_categories = one_hot_max_categories
        self.one_hot_categories_ = {}
        self.frequency_maps_ = {}
        self.reference_categories_ = {}

    def fit(self, dataframe: pd.DataFrame, categorical_columns: list[str]) -> "CategoricalEncoder":
        for column in categorical_columns:
            value_counts = dataframe[column].value_counts(dropna=False)

            if len(value_counts) <= self.one_hot_max_categories:
                reference_category = value_counts.index[0]
                self.reference_categories_[column] = reference_category
                self.one_hot_categories_[column] = [
                    category for category in value_counts.index if category != reference_category
                ]
            else:
                total_count = len(dataframe[column])
                self.frequency_maps_[column] = (value_counts / total_count).to_dict()

        return self

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        encoded_columns = []

        for column, categories in self.one_hot_categories_.items():
            for category in categories:
                dummy_name = f"{column}__{category}"
                encoded_columns.append((dataframe[column] == category).astype(int).rename(dummy_name))

        for column, frequency_map in self.frequency_maps_.items():
            default_frequency = min(frequency_map.values()) if frequency_map else 0.0
            encoded_series = dataframe[column].map(frequency_map).fillna(default_frequency)
            encoded_columns.append(encoded_series.astype(float).rename(f"{column}__frequency"))

        return pd.concat(encoded_columns, axis=1)

    def get_feature_metadata(self) -> dict:
        metadata = {}
        for column, categories in self.one_hot_categories_.items():
            metadata[column] = {
                "encoding": "one_hot",
                "reference_category": str(self.reference_categories_[column]),
                "encoded_categories": [str(category) for category in categories],
            }
        for column in self.frequency_maps_:
            metadata[column] = {"encoding": "frequency"}
        return metadata
