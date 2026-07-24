"""Sprint 2 Milestone 6: Model Comparison.

Builds a standardized comparison table across every trained candidate
model (performance, training time, complexity/explainability notes) and
generates ROC/PR/calibration/confusion-matrix visualizations
(PROJECT_CONTEXT.md Section 42).

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_model_comparison
"""

import json
import logging

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ML.ingestion.config import resolve_repo_path
from ML.modeling.experiment_log import ExperimentLog
from ML.modeling.metrics import compute_calibration_curve, compute_pr_curve, compute_roc_curve
from ML.modeling.model_registry import MODEL_REGISTRY

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")
FIGURES_DIR = MODELING_REPORTS_DIR / "figures"


def load_experiment_data():
    experiment_log = ExperimentLog.load(MODELING_REPORTS_DIR / "experiment_log.json")
    validation_probabilities = json.loads((MODELING_REPORTS_DIR / "validation_probabilities.json").read_text())
    validation_targets = json.loads((MODELING_REPORTS_DIR / "validation_targets.json").read_text())
    return experiment_log, validation_probabilities, validation_targets


def build_comparison_table(experiment_log) -> pd.DataFrame:
    rows = []
    for record in experiment_log.records:
        metrics = record.validation_metrics
        interpretability = MODEL_REGISTRY.get(record.model_name, {}).get("interpretability", "low (meta-ensemble)")
        rows.append(
            {
                "model": record.model_name,
                "interpretability": interpretability,
                "accuracy": metrics["accuracy"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "specificity": metrics["specificity"],
                "f1": metrics["f1"],
                "roc_auc": metrics["roc_auc"],
                "pr_auc": metrics["pr_auc"],
                "brier_score": metrics["brier_score"],
                "cv_roc_auc_mean": record.cross_validation["aggregated"]["roc_auc"]["mean"],
                "cv_roc_auc_std": record.cross_validation["aggregated"]["roc_auc"]["std"],
                "training_time_seconds": record.training_time_seconds,
            }
        )
    return pd.DataFrame(rows).sort_values("roc_auc", ascending=False).reset_index(drop=True)


def plot_roc_curves(validation_probabilities: dict, validation_targets: list) -> None:
    figure, axis = plt.subplots(figsize=(7, 6))
    for model_name, probabilities in validation_probabilities.items():
        curve = compute_roc_curve(validation_targets, probabilities)
        axis.plot(curve["false_positive_rate"], curve["true_positive_rate"], label=model_name)
    axis.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Chance")
    axis.set_xlabel("False Positive Rate")
    axis.set_ylabel("True Positive Rate")
    axis.set_title("ROC Curves — All Candidate Models")
    axis.legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "roc_curves.png")
    plt.close(figure)


def plot_pr_curves(validation_probabilities: dict, validation_targets: list) -> None:
    figure, axis = plt.subplots(figsize=(7, 6))
    for model_name, probabilities in validation_probabilities.items():
        curve = compute_pr_curve(validation_targets, probabilities)
        axis.plot(curve["recall"], curve["precision"], label=model_name)
    axis.set_xlabel("Recall")
    axis.set_ylabel("Precision")
    axis.set_title("Precision-Recall Curves — All Candidate Models")
    axis.legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "pr_curves.png")
    plt.close(figure)


def plot_calibration_curves(validation_probabilities: dict, validation_targets: list) -> None:
    figure, axis = plt.subplots(figsize=(7, 6))
    for model_name, probabilities in validation_probabilities.items():
        curve = compute_calibration_curve(validation_targets, probabilities)
        axis.plot(curve["mean_predicted_value"], curve["fraction_of_positives"], marker="o", label=model_name)
    axis.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfectly calibrated")
    axis.set_xlabel("Mean Predicted Probability")
    axis.set_ylabel("Fraction of Positives")
    axis.set_title("Calibration Curves — All Candidate Models")
    axis.legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "calibration_curves.png")
    plt.close(figure)


def plot_metric_comparison_bars(comparison_table: pd.DataFrame) -> None:
    metrics_to_plot = ["roc_auc", "pr_auc", "f1", "recall", "specificity"]
    figure, axis = plt.subplots(figsize=(10, 6))
    comparison_table.set_index("model")[metrics_to_plot].plot(kind="bar", ax=axis)
    axis.set_title("Validation Metric Comparison Across Models")
    axis.set_ylabel("Score")
    axis.legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES_DIR / "metric_comparison_bars.png")
    plt.close(figure)


def write_comparison_report(comparison_table: pd.DataFrame) -> None:
    lines = [
        "# Model Comparison Report",
        "",
        "Standardized comparison across every candidate model, all evaluated identically on the "
        "same validation split with the same metric suite (PROJECT_CONTEXT.md Section 42).",
        "",
        comparison_table.round(4).to_markdown(index=False),
        "",
        "## Visualizations",
        "",
        "- ROC curves: `figures/roc_curves.png`",
        "- Precision-Recall curves: `figures/pr_curves.png`",
        "- Calibration curves: `figures/calibration_curves.png`",
        "- Metric comparison bar chart: `figures/metric_comparison_bars.png`",
        "",
        "## Explainability Compatibility Notes",
        "",
        "- **High interpretability** (Logistic Regression, Decision Tree): coefficients/tree splits "
        "are directly readable; SHAP `LinearExplainer`/`TreeExplainer` both apply cleanly.",
        "- **Medium interpretability** (Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost): "
        "not directly readable, but all are tree-based ensembles fully compatible with SHAP "
        "`TreeExplainer` (exact, fast Shapley values) — verified in Milestone 12.",
        "",
    ]

    report_path = MODELING_REPORTS_DIR / "model_comparison.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Sprint 2 Milestone 6: Model Comparison")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    experiment_log, validation_probabilities, validation_targets = load_experiment_data()
    logger.info("Loaded %d model experiment records", len(experiment_log.records))

    comparison_table = build_comparison_table(experiment_log)
    comparison_table.to_csv(MODELING_REPORTS_DIR / "model_comparison.csv", index=False)
    logger.info("Wrote model_comparison.csv")
    logger.info("\n%s", comparison_table.to_string(index=False))

    plot_roc_curves(validation_probabilities, validation_targets)
    plot_pr_curves(validation_probabilities, validation_targets)
    plot_calibration_curves(validation_probabilities, validation_targets)
    plot_metric_comparison_bars(comparison_table)
    logger.info("Wrote 4 comparison figures to %s", FIGURES_DIR)

    write_comparison_report(comparison_table)

    logger.info("Sprint 2 Milestone 6 (Model Comparison) completed successfully.")


if __name__ == "__main__":
    main()
