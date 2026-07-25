"""Sprint 3 Milestone 8: Visualization Export Utility.

Exports explanations as JSON (for an API response body) and PNG (for
direct display), reusing the plotting functions from Milestones 3-4
rather than re-implementing them. This is a thin export layer, not a
second copy of the plotting logic.
"""

import json
from pathlib import Path

from ML.explainability.local_explanations import plot_decision, plot_force, plot_waterfall


def export_explanation_json(explanation: dict, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(explanation, indent=2, default=str), encoding="utf-8")
    return output_path


def export_local_visualizations(shap_values_row, feature_values_row, feature_names, expected_value, output_dir: Path) -> dict:
    """Generates all three local plot types for one row and returns their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "waterfall_plot": output_dir / "waterfall_plot.png",
        "force_plot": output_dir / "force_plot.png",
        "decision_plot": output_dir / "decision_plot.png",
    }
    plot_waterfall(shap_values_row, feature_values_row, feature_names, expected_value, paths["waterfall_plot"])
    plot_force(shap_values_row, feature_values_row, feature_names, expected_value, paths["force_plot"])
    plot_decision(shap_values_row, feature_values_row, feature_names, expected_value, paths["decision_plot"])

    return {key: str(path) for key, path in paths.items()}
