"""Scales continuous numerical variables using z-score standardization.

Only applied to genuinely continuous measurements (vitals, wait time,
visit length, counts) -- not to encoded categorical/boolean columns,
which stay as 0/1 indicators. Tree-based models (Random Forest, XGBoost,
LightGBM, CatBoost -- the project's primary candidates) are scale-
invariant and do not require this; it is provided because Logistic
Regression, also a candidate model, benefits from it, and because a
fitted scaler is a standard, reusable preprocessing artifact.

Raw (pre-scaling) values remain fully available in
Data/processed/ed2022_cleaned.parquet, and the fitted mean/std for every
column is saved in the scaler metadata, so any scaled value can be
inverse-transformed back to its original unit for interpretation.

Follows a scikit-learn-style fit/transform contract so it can be refit on
a training split only, once Milestone 7 (Train/Test Split) exists.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler


class NumericalScaler:
    def __init__(self):
        self._scaler = StandardScaler()
        self.columns_ = []

    def fit(self, dataframe: pd.DataFrame, continuous_columns: list[str]) -> "NumericalScaler":
        self.columns_ = list(continuous_columns)
        self._scaler.fit(dataframe[self.columns_].astype("float64"))
        return self

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        scaled_values = self._scaler.transform(dataframe[self.columns_].astype("float64"))
        return pd.DataFrame(scaled_values, columns=self.columns_, index=dataframe.index)

    def get_feature_metadata(self) -> dict:
        return {
            column: {"mean": float(mean), "std": float(std)}
            for column, mean, std in zip(self.columns_, self._scaler.mean_, self._scaler.scale_)
        }
