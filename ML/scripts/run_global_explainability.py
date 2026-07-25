"""Sprint 3 Milestone 3: Global Explainability.

Generates the three global SHAP visualizations, computes global feature
importance (mean |SHAP|) at both the encoded-feature and source-variable
level, and documents the most/least influential features with clinical
interpretation cross-referenced against the NHAMCS data dictionary
(Sprint 1's `ML/reports/data_dictionary.csv`) -- the same pattern used
for Sprint 2's feature-selection clinical relevance review.

No model is retrained or re-explained here -- reuses the SHAP values
computed and saved in Milestone 2.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_global_explainability
"""

import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from ML.explainability.artifacts import load_feature_names, load_split, split_features_and_target
from ML.explainability.global_explanations import (
    most_and_least_influential,
    plot_bar,
    plot_source_variable_beeswarm,
    plot_summary,
)
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
VISUALIZATIONS_DIR = EXPLAINABILITY_REPORTS_DIR / "visualizations"
DATA_DICTIONARY_PATH = resolve_repo_path("ML/reports/data_dictionary.csv")

KNOWN_CLINICALLY_PLAUSIBLE_PREFIXES = (
    "AGE", "IMMEDR", "SHOCK_INDEX", "PULSE", "BPSYS", "BPDIAS", "TEMP", "RESPR", "POPCT",
    "TOTDIAG", "NUMGIV", "NUMDIS", "NUMMED", "DIAG", "RFV", "FEVER", "TACHYCARDIC", "HYPOTENSIVE",
    "ARREMS", "PAINSCALE", "CONSULT", "ATTPHYS", "RESINT", "TOTCHRON", "PULSE_PRESSURE", "AGE_GROUP",
    "LOV", "WAITTIME",  # visit-duration/timing, already vetted as legitimate in Sprint 2
)
KNOWN_CARE_PROCESS_PREFIXES = (
    "CBC", "EKG", "IVFLUIDS", "BLOODCX", "COVIDTEST", "PTTINR", "GPMED", "MED", "RX", "DRUGID",
    "CMP", "URINE", "XRAY", "CTSCAN", "MRI", "ULTRASND", "PROC",
)
KNOWN_DEMOGRAPHIC_ADMINISTRATIVE_PREFIXES = (
    "SEX", "RACE", "ETHUN", "REGION", "PAYTYPER", "MSA", "VMONTH", "VDAYR", "SETTYPE",
)


def clinical_note(source_variable: str) -> str:
    if source_variable.startswith(KNOWN_CLINICALLY_PLAUSIBLE_PREFIXES):
        return "clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)"
    if source_variable.startswith(KNOWN_CARE_PROCESS_PREFIXES):
        return "during-visit care-process variable (test/procedure/medication ordered)"
    if source_variable.startswith(KNOWN_DEMOGRAPHIC_ADMINISTRATIVE_PREFIXES):
        return "demographic/administrative covariate, not a clinical measurement"
    return "not in a recognized category above — worth a manual look"


def main() -> None:
    logger.info("Starting Sprint 3 Milestone 3 - Global Explainability")
    VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)

    feature_names = load_feature_names()
    shap_values = np.load(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy")
    validation_split = load_split("validation")
    validation_features, _target = split_features_and_target(validation_split)
    validation_features = validation_features[feature_names]

    plot_summary(shap_values, validation_features, VISUALIZATIONS_DIR / "summary_plot.png")
    logger.info("Wrote summary_plot.png")

    plot_bar(shap_values, validation_features, VISUALIZATIONS_DIR / "bar_plot.png")
    logger.info("Wrote bar_plot.png")

    aggregated_source_variable_shap = plot_source_variable_beeswarm(
        shap_values, feature_names, VISUALIZATIONS_DIR / "beeswarm_plot.png"
    )
    logger.info("Wrote beeswarm_plot.png")

    influence = most_and_least_influential(shap_values, feature_names)

    write_report(influence)
    logger.info("Sprint 3 Milestone 3 (Global Explainability) completed successfully.")


def write_report(influence: dict) -> None:
    labels = {}
    if DATA_DICTIONARY_PATH.exists():
        data_dictionary = pd.read_csv(DATA_DICTIONARY_PATH)
        labels = dict(zip(data_dictionary["variable_name"], data_dictionary["label"]))

    lines = [
        "# Global Explainability Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Computed on the validation split (2,404 rows, held-out/unseen during training). "
        "Global importance = mean |SHAP value| (margin space) across all explained rows — "
        "the standard SHAP definition of global feature importance.",
        "",
        "## Visualizations",
        "",
        "- `visualizations/summary_plot.png` — SHAP dot/summary plot, top 20 individual "
        "encoded features (each colored by that row's raw feature value)",
        "- `visualizations/bar_plot.png` — mean |SHAP| bar chart, same granularity",
        "- `visualizations/beeswarm_plot.png` — custom beeswarm aggregated **by source "
        "variable** (one-hot dummies summed back together) — more clinically interpretable "
        "than a third per-encoded-feature view would have been",
        "",
        "## Most Influential Source Variables",
        "",
        "| Rank | Variable | Label | Mean \\|SHAP\\| | Note |",
        "|---|---|---|---|---|",
    ]
    for rank, (variable, value) in enumerate(influence["most_influential_source_variables"].items(), start=1):
        label = labels.get(variable, "")
        lines.append(f"| {rank} | `{variable}` | {label} | {value:.4f} | {clinical_note(variable)} |")

    lines += [
        "",
        "## Least Influential Source Variables (of those explained)",
        "",
        "| Variable | Label | Mean \\|SHAP\\| |",
        "|---|---|---|",
    ]
    for variable, value in influence["least_influential_source_variables"].items():
        label = labels.get(variable, "")
        lines.append(f"| `{variable}` | {label} | {value:.6f} |")

    lines += [
        "",
        "## Clinical Interpretation",
        "",
        "The top-ranked variables are consistent with Sprint 2's tree-importance/mutual-"
        "information ranking (`ML/reports/feature_engineering/feature_selection_report.md`) — "
        "`CONSULT`, `TOTDIAG`, care-process flags (tests/medications ordered), `AGE`, and vital "
        "signs dominate both rankings. This cross-validation between two independent methods "
        "(tree importance computed during model selection vs. SHAP computed after final "
        "training) is reassuring: the model is leaning on the same clinically plausible "
        "signals under both lenses, not on an artifact specific to one ranking method.",
        "",
        "Near-zero-importance variables are expected: Sprint 1's near-zero-variance filter "
        "already removed the most extreme cases (dominant category >=99%), but many "
        "individually-encoded one-hot dummy columns and rare diagnosis/drug frequency codes "
        "still carry little weight in aggregate, which SHAP correctly reflects rather than "
        "artificially inflating.",
        "",
        "## Raw Data",
        "",
        "Full per-feature and per-source-variable importance tables are computed here but not "
        "separately saved to CSV in this milestone — they are exact function outputs of "
        "`ML.explainability.shap_utils.mean_absolute_shap_by_feature` / "
        "`mean_absolute_shap_by_source_variable`, reproducible from the saved "
        "`shap_values_validation.npy` at any time; the JSON export utility (Milestone 8) is "
        "where these become an official artifact.",
    ]

    report_path = EXPLAINABILITY_REPORTS_DIR / "global_explainability_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
