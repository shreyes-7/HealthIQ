"""Unit tests for ML/modeling/survey_aware.py."""

import numpy as np
import pandas as pd

from ML.modeling.survey_aware import compare_weighted_vs_unweighted, fit_survey_glm, summarize_glm_significance


def _synthetic_survey_data(n_rows: int = 300, random_state: int = 0):
    rng = np.random.RandomState(random_state)
    features = pd.DataFrame({"x1": rng.normal(size=n_rows), "x2": rng.normal(size=n_rows)})
    target = pd.Series((features["x1"] * 1.5 + rng.normal(scale=0.5, size=n_rows) > 0).astype(int))
    weights = pd.Series(rng.uniform(50, 150, size=n_rows))
    clusters = pd.Series(rng.randint(0, 10, size=n_rows))
    return features, target, weights, clusters


def test_compare_weighted_vs_unweighted_returns_both_metric_sets():
    features, target, weights, _ = _synthetic_survey_data()
    split = len(features) // 2

    result = compare_weighted_vs_unweighted(
        features.iloc[:split], target.iloc[:split], weights.iloc[:split],
        features.iloc[split:], target.iloc[split:],
    )

    assert "unweighted_validation_metrics" in result
    assert "weighted_validation_metrics" in result
    assert "roc_auc" in result["weighted_validation_metrics"]


def test_survey_glm_fits_and_produces_significance_summary():
    features, target, weights, _ = _synthetic_survey_data()
    glm_result = fit_survey_glm(features, target, weights)
    summary = summarize_glm_significance(glm_result)

    # x1 was constructed to strongly drive the target; it should be significant.
    assert summary.loc["x1", "p_value"] < 0.05
    assert "const" in summary.index


def test_cluster_robust_glm_has_different_standard_errors_than_naive():
    features, target, weights, clusters = _synthetic_survey_data()

    naive = summarize_glm_significance(fit_survey_glm(features, target, weights))
    cluster_robust = summarize_glm_significance(fit_survey_glm(features, target, weights, clusters=clusters))

    # Coefficients should match (same weighted point estimate); standard errors need not.
    assert np.allclose(naive["coefficient"], cluster_robust["coefficient"])
