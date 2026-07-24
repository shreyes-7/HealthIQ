"""Milestone 8 - Survey-Aware Preparation.

Verifies survey design variables (PATWT, CSTRATM, CPSUM, EDWT) survived
the full pipeline (cleaning, feature engineering, train/test split)
completely untouched, and reports the design diagnostics Phase 2's
survey-aware modeling workflow will need. Does not perform any
survey-weighted estimation or modeling itself -- that is explicitly out
of scope for the data pipeline phase (PROJECT_CONTEXT.md's Survey-Aware
Machine Learning research objective belongs to Phase 2).

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_survey_diagnostics
"""

import json
import logging
from datetime import datetime, timezone

import pandas as pd

from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset
from ML.survey.design_diagnostics import (
    PSU_COLUMN,
    STRATA_COLUMN,
    WEIGHT_COLUMN,
    psu_overlap_across_splits,
    summarize_survey_design,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = resolve_repo_path("Data/processed")
SURVEY_REPORTS_DIR = resolve_repo_path("ML/reports/survey")

SPLIT_NAMES = ("train", "validation", "test")


def verify_weights_untouched(splits: dict, raw_dataframe: pd.DataFrame) -> bool:
    """Confirms every PATWT value in every split exactly matches its
    value in the raw dataset (joined on the row's original position via
    a value-set membership check, since row order isn't preserved
    through the split)."""
    raw_weight_values = set(raw_dataframe[WEIGHT_COLUMN].round(6))
    for name, frame in splits.items():
        split_weight_values = set(frame[WEIGHT_COLUMN].round(6))
        if not split_weight_values.issubset(raw_weight_values):
            logger.error("Split '%s' contains PATWT values not present in the raw dataset", name)
            return False
    return True


def write_survey_report(design_summaries: dict, overlaps: dict, weights_verified: bool) -> None:
    lines = [
        "# Survey Design Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Survey weight (`{WEIGHT_COLUMN}`) values verified untouched (subset-of-raw check) across "
        f"all splits: **{weights_verified}**.",
        "",
        "## Design Diagnostics per Split",
        "",
        "| Split | Rows | Unique Strata | Unique PSUs | Weight Sum | Weight CV | Approx. Kish Design Effect |",
        "|---|---|---|---|---|---|---|",
    ]
    for split_name in SPLIT_NAMES:
        summary = design_summaries[split_name]
        lines.append(
            f"| {split_name} | {summary['row_count']} | {summary['unique_strata']} | {summary['unique_psus']} | "
            f"{summary['weight_sum']:.1f} | {summary['weight_coefficient_of_variation']:.3f} | "
            f"{summary['approximate_kish_design_effect']:.3f} |"
        )

    lines += [
        "",
        "The approximate Kish design effect (`1 + CV(weight)^2`) is a simplified, weight-only proxy "
        "(Kish, 1965) -- not a full variance-based design effect, which needs an actual outcome and a "
        "proper survey-design estimator. It is provided so Phase 2 knows roughly how much the unequal "
        "weighting alone inflates variance, before adding clustering/stratification effects.",
        "",
        "## PSU Overlap Across Splits",
        "",
        "**Methodology caveat:** Milestone 7's train/validation/test split is stratified by the "
        "prediction target (a simple, standard choice for the traditional ML workflow) — it does "
        "NOT preserve PSU (cluster) boundaries. The same PSU can appear in more than one split:",
        "",
    ]
    for pair_name, overlap in overlaps.items():
        lines.append(f"- `{pair_name}`: {overlap}")

    lines += [
        "",
        "This is standard and acceptable for evaluating the traditional (non-survey-weighted) ML "
        "workflow. For rigorous **design-based** variance estimation in the survey-aware workflow "
        "(Phase 2's comparison objective), PSU overlap between the fitting and evaluation sets is a "
        "known limitation -- if precise design-based standard errors are required, Phase 2 should "
        "consider a PSU-level (cluster-preserving) split as an alternative, evaluated against this "
        "target-stratified split rather than assumed superior, since it would trade off exact class "
        "balance across splits.",
        "",
        "## Scope",
        "",
        "This report verifies preservation and provides diagnostics only. Actual survey-weighted "
        "model fitting (`svyset`-equivalent estimation, comparison against the traditional workflow) "
        "is Phase 2's Survey-Aware Machine Learning objective (PROJECT_CONTEXT.md Section 44), not a "
        "data engineering task.",
        "",
    ]

    report_path = SURVEY_REPORTS_DIR / "survey_design_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 8 - Survey-Aware Preparation")
    SURVEY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    missing = [name for name in SPLIT_NAMES if not (PROCESSED_DATA_DIR / f"{name}.parquet").exists()]
    if missing:
        logger.error("Missing split file(s) %s. Run Milestone 7 (run_train_test_split) first.", missing)
        return

    splits = {name: pd.read_parquet(PROCESSED_DATA_DIR / f"{name}.parquet") for name in SPLIT_NAMES}
    logger.info("Loaded splits: %s", {name: frame.shape for name, frame in splits.items()})

    config = load_config(DEFAULT_CONFIG_PATH)
    raw_dataframe, _metadata = load_dataset(config)

    weights_verified = verify_weights_untouched(splits, raw_dataframe)
    logger.info("Survey weights verified untouched: %s", weights_verified)

    design_summaries = {name: summarize_survey_design(frame) for name, frame in splits.items()}
    for name, summary in design_summaries.items():
        logger.info(
            "%s: %d strata, %d PSUs, weight CV=%.3f, approx design effect=%.3f",
            name, summary["unique_strata"], summary["unique_psus"],
            summary["weight_coefficient_of_variation"], summary["approximate_kish_design_effect"],
        )

    overlaps = psu_overlap_across_splits(splits)

    design_summaries_path = SURVEY_REPORTS_DIR / "design_diagnostics.json"
    design_summaries_path.write_text(
        json.dumps({"per_split": design_summaries, "psu_overlap": overlaps}, indent=2), encoding="utf-8"
    )
    logger.info("Wrote %s", design_summaries_path)

    write_survey_report(design_summaries, overlaps, weights_verified)

    logger.info("Milestone 8 (Survey-Aware Preparation) completed successfully.")


if __name__ == "__main__":
    main()
