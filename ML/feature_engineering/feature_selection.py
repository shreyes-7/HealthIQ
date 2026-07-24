"""Milestone 6 - Feature Selection utilities.

Ranks features by mutual information and tree-based importance. Both are
computed on the TRAINING split's features/target ONLY (never validation
or test), so the selection ranking itself cannot leak held-out
information -- the same principle Milestone 7's preprocessing split
enforces for imputation/encoding/scaling.

The RandomForest fit here is a lightweight, unsaved, unevaluated utility
used solely to rank feature importance. It is not tuned, not scored, and
not persisted as a project artifact -- it is a different thing entirely
from the properly trained, validated, and served predictive model that
Phase 2 will build. No accuracy/precision/recall/AUC is computed or
reported here, deliberately: reporting a performance metric would blur
the line between "a feature-ranking utility" and "a trained model,"
which this milestone must not cross.

Recursive Feature Elimination (RFE) is intentionally NOT run: with 800+
features, RFE requires refitting an estimator once per elimination step,
which is computationally excessive for a feature-selection utility and
largely redundant with the importance ranking already produced by the
single RandomForest fit below.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif

RANDOM_STATE = 42


def compute_mutual_information(features: pd.DataFrame, target: pd.Series) -> pd.Series:
    scores = mutual_info_classif(features, target, discrete_features=False, random_state=RANDOM_STATE)
    return pd.Series(scores, index=features.columns, name="mutual_information").sort_values(ascending=False)


def compute_tree_importance(features: pd.DataFrame, target: pd.Series) -> pd.Series:
    """Fits a lightweight RandomForest solely to rank feature importance.
    Not saved, not evaluated -- see module docstring."""
    selection_utility_model = RandomForestClassifier(
        n_estimators=200, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1
    )
    selection_utility_model.fit(features, target)
    return pd.Series(
        selection_utility_model.feature_importances_, index=features.columns, name="tree_importance"
    ).sort_values(ascending=False)


def source_variable_name(encoded_feature_name: str) -> str:
    """Maps an encoded feature name (e.g. "SEX__2", "DIAG1__frequency")
    back to its source variable ("SEX", "DIAG1") for clinically
    interpretable, per-variable aggregation."""
    return encoded_feature_name.split("__", 1)[0]


def build_feature_importance_table(mutual_information: pd.Series, tree_importance: pd.Series) -> pd.DataFrame:
    table = pd.DataFrame(
        {
            "mutual_information": mutual_information,
            "mutual_information_rank": mutual_information.rank(ascending=False, method="min"),
            "tree_importance": tree_importance.reindex(mutual_information.index),
        }
    )
    table["tree_importance_rank"] = table["tree_importance"].rank(ascending=False, method="min")
    table["combined_rank"] = (table["mutual_information_rank"] + table["tree_importance_rank"]) / 2
    table["source_variable"] = [source_variable_name(name) for name in table.index]
    return table.sort_values("combined_rank")


def aggregate_by_source_variable(feature_importance_table: pd.DataFrame) -> pd.DataFrame:
    aggregated = (
        feature_importance_table.groupby("source_variable")[["mutual_information", "tree_importance"]]
        .sum()
        .sort_values("tree_importance", ascending=False)
    )
    return aggregated
