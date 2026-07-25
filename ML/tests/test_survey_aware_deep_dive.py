"""Unit tests for the Survey-Aware Deep Dive modules:
ML/modeling/survey_aware_lightgbm.py, ML/explainability/survey_aware_shap.py,
and ML/explainability/fairness.py.
"""

import numpy as np
import pandas as pd
import pytest

from ML.explainability.fairness import compute_group_fairness_metrics, summarize_disparity
from ML.explainability.survey_aware_shap import compare_importance_rankings
from ML.modeling.survey_aware_lightgbm import fit_survey_weighted_model, get_production_hyperparameters


def test_get_production_hyperparameters_returns_lightgbm_record():
    hyperparameters = get_production_hyperparameters("lightgbm")
    assert isinstance(hyperparameters, dict)
    assert len(hyperparameters) > 0


def test_get_production_hyperparameters_raises_for_unknown_model():
    with pytest.raises(StopIteration):
        get_production_hyperparameters("not_a_real_model")


def test_fit_survey_weighted_model_uses_sample_weight():
    rng = np.random.RandomState(0)
    n_rows = 200
    features = pd.DataFrame({"x1": rng.normal(size=n_rows), "x2": rng.normal(size=n_rows)})
    target = pd.Series((features["x1"] > 0).astype(int))

    uniform_weights = pd.Series(np.ones(n_rows))
    skewed_weights = pd.Series(np.where(features["x1"] > 0, 5.0, 0.2))

    model_uniform = fit_survey_weighted_model(features, target, uniform_weights)
    model_skewed = fit_survey_weighted_model(features, target, skewed_weights)

    # Different sample weights on the same data must produce different fitted models.
    predictions_uniform = model_uniform.predict_proba(features)[:, 1]
    predictions_skewed = model_skewed.predict_proba(features)[:, 1]
    assert not np.allclose(predictions_uniform, predictions_skewed)


def test_compare_importance_rankings_identical_shap_gives_perfect_correlation():
    rng = np.random.RandomState(1)
    shap_values = rng.normal(size=(50, 4))
    feature_names = ["A", "B", "C", "D"]

    result = compare_importance_rankings(shap_values, shap_values, feature_names, top_n=4)

    assert result["spearman_rank_correlation"] == pytest.approx(1.0)
    assert result["top_n_overlap_count"] == 4
    assert result["only_in_unweighted_top_n"] == []
    assert result["only_in_weighted_top_n"] == []


def test_compare_importance_rankings_detects_reordering():
    feature_names = ["A", "B", "C"]
    # unweighted: A most important; weighted: C most important (reversed order)
    unweighted_shap = np.tile([3.0, 2.0, 1.0], (30, 1))
    weighted_shap = np.tile([1.0, 2.0, 3.0], (30, 1))

    result = compare_importance_rankings(unweighted_shap, weighted_shap, feature_names, top_n=3)

    assert result["spearman_rank_correlation"] == pytest.approx(-1.0)


def _synthetic_fairness_data():
    probabilities = np.array([0.9, 0.8, 0.1, 0.2, 0.9, 0.3, 0.6, 0.4])
    target = pd.Series([1, 1, 0, 0, 1, 0, 1, 0])
    group_labels = pd.Series(["A", "A", "A", "A", "B", "B", "B", "B"])
    return probabilities, target, group_labels


def test_compute_group_fairness_metrics_returns_one_entry_per_group():
    probabilities, target, group_labels = _synthetic_fairness_data()
    result = compute_group_fairness_metrics(probabilities, target, group_labels)

    assert set(result.keys()) == {"A", "B"}
    assert result["A"]["n"] == 4
    assert result["B"]["n"] == 4


def test_compute_group_fairness_metrics_selection_rate_matches_manual_count():
    probabilities, target, group_labels = _synthetic_fairness_data()
    result = compute_group_fairness_metrics(probabilities, target, group_labels)

    # Group A predictions at 0.5 threshold: [1, 1, 0, 0] -> selection rate 0.5
    assert result["A"]["selection_rate"] == pytest.approx(0.5)
    # Group B predictions at 0.5 threshold: [1, 0, 1, 0] -> selection rate 0.5
    assert result["B"]["selection_rate"] == pytest.approx(0.5)


def test_compute_group_fairness_metrics_handles_single_class_group():
    probabilities = np.array([0.9, 0.8, 0.7])
    target = pd.Series([1, 1, 1])  # no negatives -> FPR undefined, AUC undefined
    group_labels = pd.Series(["A", "A", "A"])

    result = compute_group_fairness_metrics(probabilities, target, group_labels)

    assert result["A"]["false_positive_rate"] is None
    assert result["A"]["roc_auc"] is None
    assert result["A"]["true_positive_rate"] == pytest.approx(1.0)


def test_summarize_disparity_computes_max_min_gap():
    group_metrics = {
        "A": {"selection_rate": 0.2, "true_positive_rate": 0.5, "false_positive_rate": 0.1, "roc_auc": 0.9},
        "B": {"selection_rate": 0.5, "true_positive_rate": 0.5, "false_positive_rate": 0.3, "roc_auc": 0.7},
    }
    summary = summarize_disparity(group_metrics)

    assert summary["selection_rate"]["gap"] == pytest.approx(0.3)
    assert summary["true_positive_rate"]["gap"] == pytest.approx(0.0)
    assert summary["roc_auc"]["gap"] == pytest.approx(0.2)


def test_summarize_disparity_skips_metrics_with_all_none_values():
    group_metrics = {
        "A": {"selection_rate": 0.2, "true_positive_rate": 0.5, "false_positive_rate": None, "roc_auc": None},
        "B": {"selection_rate": 0.4, "true_positive_rate": 0.6, "false_positive_rate": None, "roc_auc": None},
    }
    summary = summarize_disparity(group_metrics)

    assert "false_positive_rate" not in summary
    assert "roc_auc" not in summary
    assert "selection_rate" in summary
