"""Sprint 3 Milestone 3: Global Explainability.

Named `global_explanations.py` rather than the sprint plan's literal
`global.py` -- `global` is a reserved Python keyword and a module with
that name could never be imported (`import global` is a SyntaxError).

Three distinct visualizations, not three views of the same plot:
- summary_plot: SHAP's classic per-encoded-feature dot/summary plot
  (top 20 individual columns, e.g. "AGE_GROUP__older_adult_65_plus").
- bar_plot: mean |SHAP| bar chart, same per-encoded-feature granularity.
- beeswarm_plot: a custom beeswarm-style scatter AGGREGATED BY SOURCE
  VARIABLE (e.g. all "AGE_GROUP__*" dummies summed back to "AGE_GROUP").
  SHAP's native beeswarm has no built-in support for grouping one-hot
  columns back to their source variable, so this is built directly with
  matplotlib -- and is more clinically interpretable than a third
  per-encoded-feature view would have been.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from ML.explainability.shap_utils import mean_absolute_shap_by_feature, mean_absolute_shap_by_source_variable, source_variable_name

TOP_N_FEATURES_TO_PLOT = 20
TOP_N_SOURCE_VARIABLES_TO_PLOT = 20


def plot_summary(shap_values: np.ndarray, features: pd.DataFrame, output_path) -> None:
    figure = plt.figure(figsize=(9, 8))
    shap.summary_plot(shap_values, features, max_display=TOP_N_FEATURES_TO_PLOT, show=False)
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def plot_bar(shap_values: np.ndarray, features: pd.DataFrame, output_path) -> None:
    figure = plt.figure(figsize=(9, 8))
    shap.summary_plot(shap_values, features, plot_type="bar", max_display=TOP_N_FEATURES_TO_PLOT, show=False)
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def plot_source_variable_beeswarm(shap_values: np.ndarray, feature_names: list[str], output_path) -> pd.DataFrame:
    """Aggregates each row's SHAP contribution by source variable (summing
    across its one-hot dummy columns), then draws a beeswarm-style
    scatter: one row of points per source variable, x-position = that
    row's aggregated SHAP value, colored by whether the aggregated
    contribution pushed the prediction up or down."""
    source_variables = pd.Index([source_variable_name(name) for name in feature_names])
    aggregated = pd.DataFrame(shap_values, columns=feature_names).T.groupby(source_variables).sum().T

    ranking = mean_absolute_shap_by_source_variable(shap_values, feature_names)
    top_variables = ranking.head(TOP_N_SOURCE_VARIABLES_TO_PLOT).index.tolist()

    figure, axis = plt.subplots(figsize=(9, 8))
    rng = np.random.default_rng(42)
    for row_index, variable in enumerate(reversed(top_variables)):
        values = aggregated[variable].values
        jitter = rng.uniform(-0.3, 0.3, size=len(values))
        colors = np.where(values >= 0, "#d62728", "#1f77b4")
        axis.scatter(values, np.full_like(values, row_index, dtype=float) + jitter, s=6, alpha=0.5, c=colors)

    axis.set_yticks(range(len(top_variables)))
    axis.set_yticklabels(list(reversed(top_variables)))
    axis.axvline(0, color="grey", linewidth=0.8)
    axis.set_xlabel("SHAP value (margin/log-odds space), aggregated per source variable")
    axis.set_title("Source-Variable Beeswarm (red = pushes toward admission, blue = pushes away)")
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)

    return aggregated[top_variables]


def most_and_least_influential(shap_values: np.ndarray, feature_names: list[str], top_n: int = 15) -> dict:
    per_feature = mean_absolute_shap_by_feature(shap_values, feature_names)
    per_source_variable = mean_absolute_shap_by_source_variable(shap_values, feature_names)
    return {
        "most_influential_features": per_feature.head(top_n).to_dict(),
        "least_influential_features": per_feature.tail(top_n).to_dict(),
        "most_influential_source_variables": per_source_variable.head(top_n).to_dict(),
        "least_influential_source_variables": per_source_variable.tail(top_n).to_dict(),
    }
