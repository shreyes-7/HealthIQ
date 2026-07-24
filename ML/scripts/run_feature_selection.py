"""Milestone 6 - Feature Selection.

Ranks the training split's features by mutual information and tree-based
importance (computed on the TRAINING split only, never validation/test),
aggregates importance back to each feature's source variable for
clinical interpretability, and documents a relevance review referencing
the data dictionary. RFE is deliberately skipped (see
ML/feature_engineering/feature_selection.py). No model is trained or
evaluated -- the RandomForest fit here is a lightweight, discarded
ranking utility only.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_feature_selection
"""

import logging
from datetime import datetime, timezone

import pandas as pd

from ML.feature_engineering.feature_selection import (
    aggregate_by_source_variable,
    build_feature_importance_table,
    compute_mutual_information,
    compute_tree_importance,
)
from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TRAIN_DATASET_PATH = resolve_repo_path("Data/processed/train.parquet")
DATA_DICTIONARY_PATH = resolve_repo_path("ML/reports/data_dictionary.csv")
FEATURE_SELECTION_REPORTS_DIR = resolve_repo_path("ML/reports/feature_engineering")

NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}


def load_train_features_and_target() -> tuple[pd.DataFrame, pd.Series]:
    train_dataframe = pd.read_parquet(TRAIN_DATASET_PATH)
    feature_columns = [column for column in train_dataframe.columns if column not in NON_FEATURE_COLUMNS]
    return train_dataframe[feature_columns], train_dataframe[TARGET_COLUMN_NAME]


def write_feature_selection_report(
    feature_importance_table: pd.DataFrame, source_variable_ranking: pd.DataFrame, top_n: int = 25
) -> None:
    labels = {}
    if DATA_DICTIONARY_PATH.exists():
        data_dictionary = pd.read_csv(DATA_DICTIONARY_PATH)
        labels = dict(zip(data_dictionary["variable_name"], data_dictionary["label"]))

    lines = [
        "# Feature Selection Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Computed on the training split only ({TRAIN_DATASET_PATH.name}) — mutual information "
        "and tree-based importance never see validation or test data, so the selection ranking "
        "itself cannot leak held-out information.",
        "",
        "**No model was trained or evaluated.** The RandomForest used to compute tree importance "
        "is a lightweight, unsaved, unscored ranking utility (see "
        "`ML/feature_engineering/feature_selection.py` docstring) — a different thing from the "
        "properly trained and validated predictive model Phase 2 will build.",
        "",
        "## Method",
        "",
        "- **Mutual Information** (`sklearn.feature_selection.mutual_info_classif`): target-aware, "
        "model-free, captures non-linear relationships.",
        "- **Tree-based Importance** (`RandomForestClassifier`, 200 trees, max_depth=12): captures "
        "interactions the univariate mutual-information score misses.",
        "- **Recursive Feature Elimination: skipped.** With 800+ encoded features, RFE requires "
        "refitting an estimator once per elimination step — computationally excessive for a "
        "selection utility and largely redundant with the importance ranking above.",
        "- **Clinical relevance review**: automated only to the extent of cross-referencing top-ranked "
        "source variables against their NHAMCS codebook label (`ML/reports/data_dictionary.csv`); a "
        "genuine clinical-expert review is not an automatable step and remains open.",
        "",
        f"## Top {top_n} Features by Combined Rank (encoded, individual)",
        "",
        "| Rank | Feature | Source Variable | Mutual Info | Tree Importance |",
        "|---|---|---|---|---|",
    ]
    for rank, (feature_name, row) in enumerate(feature_importance_table.head(top_n).iterrows(), start=1):
        lines.append(
            f"| {rank} | `{feature_name}` | `{row['source_variable']}` | "
            f"{row['mutual_information']:.4f} | {row['tree_importance']:.4f} |"
        )

    lines += [
        "",
        f"## Top {top_n} Source Variables (aggregated across their encoded columns)",
        "",
        "This view is more clinically interpretable: one-hot encoding splits a single source "
        "variable (e.g. `AGE_GROUP`) across several dummy columns, diluting its individual-column "
        "rank above. Aggregating recovers each variable's total contribution.",
        "",
        "| Rank | Variable | Label (from data dictionary) | Mutual Info (sum) | Tree Importance (sum) |",
        "|---|---|---|---|---|",
    ]
    for rank, (variable, row) in enumerate(source_variable_ranking.head(top_n).iterrows(), start=1):
        label = labels.get(variable, "")
        lines.append(
            f"| {rank} | `{variable}` | {label} | {row['mutual_information']:.4f} | {row['tree_importance']:.4f} |"
        )

    lines += [
        "",
        "## Clinical Relevance Commentary",
        "",
        "The top-ranked source variables were cross-checked against well-established emergency "
        "medicine admission risk factors (age, triage acuity, vital-sign abnormality, comorbidity "
        "burden, diagnosis, and care intensity during the visit) rather than an exhaustive "
        "literature review. One finding is worth calling out explicitly: `CONSULT` ranked #1 and "
        "was manually re-verified against the codebook before accepting it, since a "
        "\"consulting physician\" sounded like it could be disposition-adjacent leakage similar to "
        "the already-excluded `ADMTPHYS` (admitting physician). It is not: `CONSULT` is part of "
        "the codebook's \"PROVIDERS SEEN\" item block (item 219, alongside `ATTPHYS`/`RESINT`/"
        "`RNLPN`/etc.) — a during-visit care-process flag recording who saw the patient, "
        "structurally distinct from the post-admission `ADMTPHYS`. Diagnostic/procedure flags "
        "(`CBC`, `EKG`, `IVFLUIDS`, `BLOODCX`, `COVIDTEST`, `PTTINR`, `TOTDIAG`) are similarly "
        "legitimate: tests ordered during the visit inform the disposition decision rather than "
        "resulting from it, the same reasoning already applied to `TOTDIAG` in Milestone 5.",
        "",
    ]
    known_clinically_plausible_prefixes = (
        "AGE", "IMMEDR", "SHOCK_INDEX", "PULSE", "BPSYS", "BPDIAS", "TEMP", "RESPR", "POPCT",
        "TOTDIAG", "NUMGIV", "NUMDIS", "NUMMED", "DIAG", "RFV", "FEVER", "TACHYCARDIC", "HYPOTENSIVE",
        "ARREMS", "PAINSCALE", "CONSULT", "ATTPHYS", "RESINT", "TOTCHRON", "IMMEDR",
    )
    known_care_process_prefixes = (
        "CBC", "EKG", "IVFLUIDS", "BLOODCX", "COVIDTEST", "PTTINR", "GPMED", "MED", "RX", "DRUGID",
        "CMP", "URINE", "XRAY", "CTSCAN", "MRI", "ULTRASND",
    )
    for variable in source_variable_ranking.head(top_n).index:
        if variable.startswith(known_clinically_plausible_prefixes):
            note = "clinically expected (age, triage acuity, vitals, comorbidity, or diagnosis)"
        elif variable.startswith(known_care_process_prefixes):
            note = "during-visit care-process variable (test/procedure/medication ordered) — informs, does not follow from, the disposition decision"
        else:
            note = "plausible but not in a recognized clinical category above — worth a manual look"
        lines.append(f"- `{variable}`: {note}")

    lines += [
        "",
        "## Full Rankings",
        "",
        "- Per-encoded-feature: `ML/reports/feature_engineering/feature_importance_scores.csv`",
        "- Per-source-variable: `ML/reports/feature_engineering/source_variable_importance.csv`",
        "",
        "## Recommendation",
        "",
        "A ranked list, not a hard cutoff, is provided deliberately: the right feature count "
        "depends on the model family Phase 2 chooses (tree ensembles tolerate many weak features "
        "better than Logistic Regression does). `combined_rank` in the CSV gives a reasonable "
        "starting point for a top-K selection if one is needed.",
        "",
    ]

    report_path = FEATURE_SELECTION_REPORTS_DIR / "feature_selection_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 6 - Feature Selection")
    FEATURE_SELECTION_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if not TRAIN_DATASET_PATH.exists():
        logger.error("Training split not found at %s. Run Milestone 7 (run_train_test_split) first.", TRAIN_DATASET_PATH)
        return

    features, target = load_train_features_and_target()
    logger.info("Loaded training features %s and target (%d positive / %d total)", features.shape, int(target.sum()), len(target))

    mutual_information = compute_mutual_information(features, target)
    logger.info("Computed mutual information for %d features", len(mutual_information))

    tree_importance = compute_tree_importance(features, target)
    logger.info("Computed tree-based importance for %d features (lightweight, unsaved utility fit)", len(tree_importance))

    feature_importance_table = build_feature_importance_table(mutual_information, tree_importance)
    feature_importance_table.to_csv(FEATURE_SELECTION_REPORTS_DIR / "feature_importance_scores.csv")
    logger.info("Wrote feature_importance_scores.csv")

    source_variable_ranking = aggregate_by_source_variable(feature_importance_table)
    source_variable_ranking.to_csv(FEATURE_SELECTION_REPORTS_DIR / "source_variable_importance.csv")
    logger.info("Wrote source_variable_importance.csv")

    write_feature_selection_report(feature_importance_table, source_variable_ranking)

    logger.info("Milestone 6 (Feature Selection) completed successfully.")


if __name__ == "__main__":
    main()
