"""Unit tests for ML/modeling/cross_validation.py."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from ML.modeling.cross_validation import cross_validate_model


def _synthetic_classification_data(n_rows: int = 200, n_features: int = 5, random_state: int = 0):
    rng = np.random.RandomState(random_state)
    features = pd.DataFrame(rng.normal(size=(n_rows, n_features)), columns=[f"f{i}" for i in range(n_features)])
    # Target correlated with f0 so the model can learn something above chance.
    target = pd.Series((features["f0"] + rng.normal(scale=0.5, size=n_rows) > 0).astype(int))
    return features, target


def test_cross_validate_returns_one_fold_metric_per_fold():
    features, target = _synthetic_classification_data()
    result = cross_validate_model(LogisticRegression(), features, target, n_folds=4)

    assert len(result["fold_metrics"]) == 4
    assert result["n_folds"] == 4


def test_cross_validate_aggregates_mean_and_std():
    features, target = _synthetic_classification_data()
    result = cross_validate_model(LogisticRegression(), features, target, n_folds=5)

    assert "mean" in result["aggregated"]["roc_auc"]
    assert "std" in result["aggregated"]["roc_auc"]
    assert 0.5 <= result["aggregated"]["roc_auc"]["mean"] <= 1.0


def test_cross_validate_is_deterministic_with_fixed_seed():
    features, target = _synthetic_classification_data()

    result_a = cross_validate_model(LogisticRegression(), features, target, n_folds=3)
    result_b = cross_validate_model(LogisticRegression(), features, target, n_folds=3)

    assert result_a["aggregated"]["roc_auc"]["mean"] == result_b["aggregated"]["roc_auc"]["mean"]
