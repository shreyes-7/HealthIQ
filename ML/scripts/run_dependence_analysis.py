"""Sprint 3 Milestone 5: Dependence Analysis.

Generates SHAP dependence plots for the top 3 features by global
importance (mean |SHAP|) plus additional important variables, prioritizing
continuous features -- they show a real curve (nonlinear/threshold
effects); one-hot dummy columns just show two point clouds. Documents
observed nonlinear effects, threshold effects, and interactions.

No model is retrained here -- reuses the SHAP values from Milestone 2.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_dependence_analysis
"""

import logging
from datetime import datetime, timezone

import numpy as np

from ML.explainability.artifacts import load_feature_names, load_split, split_features_and_target
from ML.explainability.dependence import is_effectively_continuous, plot_dependence
from ML.explainability.shap_utils import mean_absolute_shap_by_feature
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
DEPENDENCE_PLOTS_DIR = EXPLAINABILITY_REPORTS_DIR / "dependence_plots"

ADDITIONAL_VARIABLES_TO_PLOT = 5


def main() -> None:
    logger.info("Starting Sprint 3 Milestone 5 - Dependence Analysis")
    DEPENDENCE_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    feature_names = load_feature_names()
    shap_values = np.load(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy")
    validation_split = load_split("validation")
    validation_features, _target = split_features_and_target(validation_split)
    validation_features = validation_features[feature_names]

    ranking = mean_absolute_shap_by_feature(shap_values, feature_names)
    top_3 = ranking.head(3).index.tolist()
    logger.info("Top 3 features: %s", top_3)

    remaining_ranked = ranking.index[3:]
    additional_continuous = [
        name for name in remaining_ranked if is_effectively_continuous(validation_features[name])
    ][:ADDITIONAL_VARIABLES_TO_PLOT]
    logger.info("Additional continuous variables: %s", additional_continuous)

    all_plotted = top_3 + additional_continuous
    for feature_name in all_plotted:
        output_path = DEPENDENCE_PLOTS_DIR / f"{feature_name.replace('/', '_')}_dependence.png"
        plot_dependence(feature_name, shap_values, validation_features, output_path)
        logger.info("Wrote %s", output_path.name)

    write_report(top_3, additional_continuous, ranking, validation_features, shap_values, feature_names)
    logger.info("Sprint 3 Milestone 5 (Dependence Analysis) completed successfully.")


def write_report(top_3, additional_continuous, ranking, features, shap_values, feature_names) -> None:
    lines = [
        "# Dependence Analysis Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Dependence plots for the top 3 features by global importance, plus additional "
        "important **continuous** variables (prioritized over one-hot dummies, which only "
        "show two point clouds rather than a traceable curve). Each plot is auto-colored by "
        "SHAP's chosen interaction feature.",
        "",
        f"Top 3: {top_3}",
        f"Additional: {additional_continuous}",
        "",
        "## Observations",
        "",
    ]

    for feature_name in top_3 + additional_continuous:
        values = features[feature_name]
        feature_shap = shap_values[:, feature_names.index(feature_name)]
        correlation = float(np.corrcoef(values, feature_shap)[0, 1]) if values.nunique() > 1 else float("nan")
        lines.append(
            f"- `{feature_name}`: value range [{values.min():.2f}, {values.max():.2f}], "
            f"Pearson correlation between raw value and SHAP contribution: {correlation:.3f} "
            f"({'roughly monotonic/linear' if abs(correlation) > 0.6 else 'nonlinear or threshold-like relationship — see plot'})"
        )

    lines += [
        "",
        "See `dependence_plots/*.png` for the actual shape of each relationship — a single "
        "correlation number above cannot distinguish a threshold effect from a smooth "
        "nonlinear one; the plots are the primary artifact here, this table is a navigation aid.",
    ]

    report_path = EXPLAINABILITY_REPORTS_DIR / "dependence_analysis_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
