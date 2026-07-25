"""Sprint 3 Milestone 2: SHAP Integration.

Detects the model type and builds the appropriate SHAP explainer, then
computes SHAP values. Confirmed empirically (not assumed) against this
project's specific model/library versions (LightGBM 4.7.0, SHAP 0.52.0):

- `shap.TreeExplainer(model).shap_values(X)` returns a single ndarray of
  shape (n_samples, n_features) for this LightGBM binary classifier --
  NOT a list of per-class arrays, despite the UserWarning SHAP emits
  ("shap values output has changed to a list of ndarray"). That warning
  describes a historical LightGBM-side change SHAP is warning about, not
  this call's actual return type -- verified directly before writing this
  module.
- Values are in MARGIN (log-odds) space: `shap_values.sum(axis=1) +
  explainer.expected_value` reconstructs `model.predict(X, raw_score=True)`
  exactly (max abs diff ~3e-9), and its sigmoid reconstructs
  `predict_proba` exactly. See ML.explainability.shap_utils for the
  probability-space conversion used everywhere a human-readable
  contribution is shown.
"""

import shap

# Substring markers for tree-based model class names. TreeExplainer is
# exact and fast for these; anything else falls back to a model-agnostic
# explainer so this module keeps working if the selected model changes.
TREE_BASED_MARKERS = ("Forest", "Boost", "Tree", "CatBoost", "LGBM", "XGB")
LINEAR_MODEL_MARKERS = ("LogisticRegression", "LinearRegression")


def detect_model_family(model) -> str:
    """Returns 'tree', 'linear', or 'other' based on the model's class name."""
    model_type_name = type(model).__name__
    if any(marker in model_type_name for marker in TREE_BASED_MARKERS):
        return "tree"
    if any(marker in model_type_name for marker in LINEAR_MODEL_MARKERS):
        return "linear"
    return "other"


def build_explainer(model, background_data=None):
    """Builds the appropriate SHAP explainer for the model's family.

    `background_data` is only required for the linear/model-agnostic
    paths -- TreeExplainer computes exact values directly from the tree
    structure (feature_perturbation="tree_path_dependent" by default) and
    needs no background sample.
    """
    family = detect_model_family(model)

    if family == "tree":
        return shap.TreeExplainer(model)
    if family == "linear":
        if background_data is None:
            raise ValueError("LinearExplainer requires background_data.")
        return shap.LinearExplainer(model, background_data)

    if background_data is None:
        raise ValueError("Model-agnostic Explainer requires background_data.")
    return shap.Explainer(model.predict_proba, background_data)


def compute_shap_values(explainer, features):
    """Computes SHAP values for `features` (a DataFrame of model-ready
    columns, in the model's expected order). Returns a 2D array of shape
    (n_samples, n_features), in margin (log-odds) space for tree models."""
    return explainer.shap_values(features)
