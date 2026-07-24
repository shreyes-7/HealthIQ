"""Sprint 2 Milestone 8: a first-pass survey-aware model, comparing
against the conventional (unweighted) Logistic Regression baseline.

This is explicitly scoped as a first pass, not the full research program
PROJECT_CONTEXT.md Section 44 envisions (which calls for running both
traditional and survey-aware experiments under identical preprocessing
"whenever possible" and comparing generalization/fairness/explanation
stability, not just point predictions). Two comparisons are made here:

1. Predictive comparison (full feature set): the same LogisticRegression
   used as the conventional baseline, refit with `sample_weight=PATWT`.
   This incorporates the WEIGHT component of the survey design so
   predictions better reflect the U.S. population NHAMCS represents,
   directly comparable to the unweighted baseline using the same metric
   suite.
2. Inference comparison (focused feature subset): a statsmodels weighted
   GLM with cluster-robust standard errors (clustering on CPSUM, the PSU
   variable) against the same GLM without the cluster correction. This
   is the part plain `sample_weight` cannot capture -- whether accounting
   for the clustered sample design changes which predictors appear
   statistically significant. Restricted to a small, clinically
   interpretable feature subset (Sprint 1's top-ranked features): fitting
   this on all 866 encoded features would be both statistically unstable
   at this sample size and defeat the interpretability point of doing it.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

from ML.modeling.metrics import compute_classification_metrics

RANDOM_STATE = 42
FOCUSED_FEATURE_COUNT = 15


def fit_weighted_logistic_regression(features: pd.DataFrame, target: pd.Series, weights: pd.Series) -> LogisticRegression:
    model = LogisticRegression(solver="liblinear", max_iter=1000, random_state=RANDOM_STATE)
    model.fit(features, target, sample_weight=weights)
    return model


def compare_weighted_vs_unweighted(
    features_train: pd.DataFrame,
    target_train: pd.Series,
    weights_train: pd.Series,
    features_val: pd.DataFrame,
    target_val: pd.Series,
) -> dict:
    unweighted_model = LogisticRegression(solver="liblinear", max_iter=1000, random_state=RANDOM_STATE)
    unweighted_model.fit(features_train, target_train)
    unweighted_metrics = compute_classification_metrics(
        target_val, unweighted_model.predict_proba(features_val)[:, 1]
    )

    weighted_model = fit_weighted_logistic_regression(features_train, target_train, weights_train)
    weighted_metrics = compute_classification_metrics(target_val, weighted_model.predict_proba(features_val)[:, 1])

    return {
        "unweighted_validation_metrics": unweighted_metrics,
        "weighted_validation_metrics": weighted_metrics,
    }


def select_focused_features(feature_importance_path, feature_columns: list[str], top_n: int = FOCUSED_FEATURE_COUNT) -> list[str]:
    """Picks a small, clinically interpretable feature subset for the GLM
    inference comparison, using Sprint 1's feature importance ranking."""
    importance = pd.read_csv(feature_importance_path, index_col=0)
    ranked = importance.sort_values("combined_rank")
    focused = [name for name in ranked.index if name in feature_columns][:top_n]
    return focused


def fit_survey_glm(
    features: pd.DataFrame, target: pd.Series, weights: pd.Series, clusters: pd.Series = None
):
    """Fits a weighted logistic GLM, optionally with cluster-robust
    standard errors. Returns the fitted statsmodels results object.

    Uses `var_weights` rather than `freq_weights`: survey weights like
    PATWT represent inverse selection probability, not literal duplicate
    observation counts, so they must not inflate the effective sample
    size used in variance calculations the way `freq_weights` would.

    KNOWN LIMITATION: statsmodels emits `SpecificationWarning: cov_type
    not fully supported with var_weights` for the cluster-robust fit
    below -- this is a genuine, documented statsmodels constraint (not
    specific to this weight choice; freq_weights hits the same warning),
    not a bug in this code. The resulting cluster-robust standard errors
    should be read as exploratory/approximate, not textbook-rigorous
    design-based inference. A dedicated survey-design library (e.g.
    `samplics`) would be needed for that; using one is out of scope for
    this first-pass comparison (see module docstring)."""
    design_matrix = sm.add_constant(features.astype(float))
    model = sm.GLM(target.astype(float), design_matrix, family=sm.families.Binomial(), var_weights=weights.astype(float))

    if clusters is not None:
        return model.fit(cov_type="cluster", cov_kwds={"groups": clusters})
    return model.fit()


def summarize_glm_significance(glm_results) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "coefficient": glm_results.params,
            "std_error": glm_results.bse,
            "p_value": glm_results.pvalues,
            "significant_at_0.05": glm_results.pvalues < 0.05,
        }
    )
