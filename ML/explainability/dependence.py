"""Sprint 3 Milestone 5: Dependence Analysis.

SHAP dependence plots for the top-ranked features (plus a curated set of
additional important variables), each auto-colored by SHAP's chosen
interaction feature -- surfaces nonlinear effects, threshold effects, and
feature interactions that a single global-importance number can't show.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


def plot_dependence(feature_name: str, shap_values: np.ndarray, features: pd.DataFrame, output_path) -> None:
    figure, axis = plt.subplots(figsize=(8, 6))
    shap.dependence_plot(feature_name, shap_values, features, ax=axis, show=False)
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def is_effectively_continuous(series: pd.Series, min_unique: int = 8) -> bool:
    """Dependence plots are most informative for continuous features
    (a real x-axis to trace a curve along); binary one-hot dummies just
    show two point clouds. Used to prioritize which "additional important
    variables" get a plot."""
    return series.nunique() >= min_unique
