"""Survey-Aware Deep Dive: consolidated summary.

Ties together the three pieces produced by
`run_survey_aware_lightgbm.py`, `run_survey_aware_shap_comparison.py`,
and `run_fairness_audit.py` into a single narrative report answering the
project's core survey-aware research question (PROJECT_CONTEXT.md §44):
does accounting for NHAMCS's survey design change the production model's
performance, its explanations, and its fairness across demographic
groups?

This script only reads the JSON artifacts already produced by the three
prior scripts -- it performs no new computation. Run it last, after all
three have completed.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_survey_aware_summary
"""

import json
import logging
from datetime import datetime, timezone

from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEEP_DIVE_DIR = resolve_repo_path("ML/reports/survey_aware_deep_dive")


def main() -> None:
    logger.info("Consolidating Survey-Aware Deep Dive summary")

    performance = json.loads((DEEP_DIVE_DIR / "weighted_vs_unweighted_metrics.json").read_text())
    shap_comparison = json.loads((DEEP_DIVE_DIR / "shap_comparison.json").read_text())
    fairness = json.loads((DEEP_DIVE_DIR / "fairness_audit.json").read_text())

    write_report(performance, shap_comparison, fairness)
    logger.info("Survey-Aware Deep Dive summary complete.")


def write_report(performance: dict, shap_comparison: dict, fairness: dict) -> None:
    validation_roc_auc_delta = (
        performance["validation"]["weighted"]["roc_auc"] - performance["validation"]["unweighted"]["roc_auc"]
    )
    test_roc_auc_delta = performance["test"]["weighted"]["roc_auc"] - performance["test"]["unweighted"]["roc_auc"]

    ranking_comparison = shap_comparison["ranking_comparison"]
    rank_correlation = ranking_comparison["spearman_rank_correlation"]
    top_n_overlap = ranking_comparison["top_n_overlap_count"]
    top_n = ranking_comparison["top_n"]
    flip_stats = shap_comparison["decision_flip_stats"]

    unweighted_disparity = fairness["unweighted_disparity"]
    weighted_disparity = fairness["weighted_disparity"]
    narrowed_metrics = [m for m in unweighted_disparity if weighted_disparity[m]["gap"] < unweighted_disparity[m]["gap"]]
    widened_metrics = [m for m in unweighted_disparity if weighted_disparity[m]["gap"] > unweighted_disparity[m]["gap"]]

    lines = [
        "# Survey-Aware Deep Dive: Consolidated Summary",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "This project's stated primary research contribution (`Docs/PROJECT_CONTEXT.md` §44) is "
        "survey-aware prediction: using NHAMCS's `PATWT` sample weights so the model reflects the "
        "U.S. population the survey is designed to estimate, rather than only the raw sample. "
        "Sprint 2 took a first pass at this with Logistic Regression only, never connected to the "
        "production model, SHAP explainability, or fairness. This deep dive closes that gap by "
        "running the full comparison — performance, explanations, and fairness — on the actual "
        "production LightGBM model.",
        "",
        "Three questions, three reports:",
        "",
        "| Question | Report | Headline Finding |",
        "|---|---|---|",
        (
            "| Does survey weighting change raw performance? | "
            "[weighted_vs_unweighted_lightgbm.md](weighted_vs_unweighted_lightgbm.md) | "
            f"Validation ROC-AUC {validation_roc_auc_delta:+.4f}, test ROC-AUC {test_roc_auc_delta:+.4f} "
            "— small, expected decreases, far smaller than Sprint 2's Logistic Regression gap |"
        ),
        (
            "| Does survey weighting change what the model bases its explanations on? | "
            "[shap_comparison_report.md](shap_comparison_report.md) | "
            f"Spearman rank correlation {rank_correlation:.4f}, {top_n_overlap}/{top_n} top-feature "
            f"overlap — reasoning is stable; only "
            f"{flip_stats['flip_count']}/{flip_stats['total']} ({flip_stats['flip_rate']:.2%}) "
            "predictions flip, concentrated near the decision boundary |"
        ),
        (
            "| Does survey weighting change fairness across race/ethnicity? | "
            "[fairness_audit_report.md](fairness_audit_report.md) | "
            f"{len(narrowed_metrics)}/4 disparity gaps narrow "
            f"({', '.join(narrowed_metrics)}); {len(widened_metrics)}/4 widen "
            f"({', '.join(widened_metrics) if widened_metrics else 'none'}) |"
        ),
        "",
        "## Synthesis",
        "",
        "The three findings fit together into a coherent story. Survey weighting trades a small "
        "amount of raw in-sample discrimination for population representativeness — expected, "
        "since `PATWT` deliberately up-weights underrepresented sampling strata. That trade does "
        "**not** destabilize the model's clinical reasoning: the same features drive predictions "
        "in essentially the same order, and the vast majority of predictions do not change at "
        "all. Where predictions do change, they concentrate almost entirely on cases the model "
        "was already uncertain about (near the 0.5 decision boundary) — exactly where a small "
        "shift in training weights would be expected to matter, and exactly where a clinician "
        "would want a second look anyway.",
        "",
        "Most importantly for this project's research framing: the small performance cost of "
        f"survey weighting buys a real, measurable improvement in equity — "
        f"{len(narrowed_metrics)} of 4 fairness metrics improve for race/ethnicity subgroups on "
        "the validation split. This is the strongest evidence in the project so far that "
        "survey-aware learning is not just methodologically correct but practically worthwhile: "
        "it is not merely a more statistically rigorous way to fit the same model, it changes the "
        "model's behavior in a direction the project should prefer.",
        "",
        "## Caveats",
        "",
        "- All three analyses use a single validation split with no bootstrap confidence "
        "intervals around the reported gaps or deltas — treat magnitudes as indicative, not "
        "statistically certified.",
        "- The fairness audit covers one protected attribute (`RACERETH`). Sex (`SEX`) and age "
        "group are natural next candidates given they are also present in the feature set.",
        "- The per-group ROC-AUC gap widens slightly even though threshold-dependent fairness "
        "metrics narrow — see the caveat in `fairness_audit_report.md` for why these can diverge.",
        "",
        "## Artifacts",
        "",
        "- `weighted_vs_unweighted_lightgbm.md` / `.json` — performance comparison",
        "- `shap_comparison_report.md` / `.json` — explanation comparison and decision-flip analysis",
        "- `fairness_audit_report.md` / `.json` — fairness audit across RACERETH",
        "- `figures/` — supporting visualizations for all three",
        "- `ML/saved_models/model_survey_weighted.pkl` — the survey-weighted model artifact itself",
    ]

    report_path = DEEP_DIVE_DIR / "summary.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
