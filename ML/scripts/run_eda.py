"""Milestone 2 - Exploratory Data Analysis.

Generates missing-value, duplicate, numerical, categorical, class-imbalance,
correlation, and outlier reports, plus a curated set of distribution plots.

Read-only: the raw dataset is never modified and no cleaning is performed.
Cleaning decisions (sentinel-code recoding, imputation, outlier handling)
are deferred to Milestone 4.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_eda
"""

import json
import logging
from datetime import datetime, timezone

from ML.eda.categorical_summary import build_categorical_summary
from ML.eda.class_imbalance import analyze_class_imbalance, compute_derived_target
from ML.eda.correlation import build_correlation_matrix, target_correlation, top_correlated_pairs
from ML.eda.distributions import (
    KEY_CATEGORICAL_VARIABLES,
    KEY_NUMERICAL_VARIABLES,
    plot_categorical_distributions,
    plot_correlation_heatmap,
    plot_missing_value_heatmap,
    plot_numerical_distributions,
    plot_target_distribution,
)
from ML.eda.duplicates import analyze_duplicates
from ML.eda.missing_values import build_missing_value_report, summarize_missing_values
from ML.eda.numerical_summary import build_numerical_summary
from ML.eda.type_classification import split_columns_by_type
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EDA_REPORTS_DIR = resolve_repo_path("ML/reports/eda")
FIGURES_DIR = EDA_REPORTS_DIR / "figures"


def write_eda_report(
    dataframe,
    numerical_columns,
    categorical_columns,
    missing_summary,
    duplicate_summary,
    class_imbalance,
    top_pairs,
    target_corr,
    numerical_plots,
    categorical_plots,
    target_plot,
    heatmap_plot,
    missing_heatmap_plot,
) -> None:
    lines = [
        "# Exploratory Data Analysis Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Dataset shape: {dataframe.shape[0]} rows x {dataframe.shape[1]} columns.",
        f"Classified as {len(numerical_columns)} numerical and {len(categorical_columns)} categorical "
        f"variables (see `ML/eda/type_classification.py` for the classification rule).",
        "",
        "## 1. Missing Value Analysis",
        "",
        f"- Total missing cells: {missing_summary['total_missing_cells']:,} / {missing_summary['total_cells']:,} "
        f"({missing_summary['overall_missing_percentage']}%)",
        f"- Columns with no missing values: {missing_summary['columns_with_no_missing_values']}",
        f"- Columns with more than 50% missing: {missing_summary['columns_over_50_percent_missing']}",
        f"- Fully missing columns: {missing_summary['fully_missing_columns'] or 'none'}",
        "- Full per-variable detail: `missing_values_report.csv`",
        f"- Heatmap (top 30 columns by missing %): `figures/{missing_heatmap_plot}`",
        "",
        "## 2. Duplicate Analysis",
        "",
        f"- Fully duplicate rows: {duplicate_summary['duplicate_row_count']} "
        f"({duplicate_summary['duplicate_row_percentage']}%)",
        "",
        "## 3. Numerical Summaries",
        "",
        "Per-variable count, mean, std, min/p25/median/p75/max, negative-sentinel-code "
        "count, and IQR-based outlier count: `numerical_summary.csv`.",
        "",
        "**Important caveat:** NHAMCS commonly encodes Not-applicable/Unknown/Blank as "
        "negative sentinel values (e.g. -7, -8, -9) rather than as NaN. These distort "
        "mean/std/outlier statistics wherever they occur — see the `negative_value_count` "
        "column. No recoding is performed at this stage (deferred to Milestone 4).",
        "",
        "## 4. Categorical Summaries",
        "",
        "Per-variable cardinality, missing percentage, top 5 categories, and rare-category "
        f"count (categories under 1% frequency): `categorical_summary.csv`.",
        "",
        "## 5. Class Imbalance Analysis",
        "",
        f"Target: `{list(class_imbalance['counts'].keys())}` derived as "
        "`ADMITHOS == 1 or OBSHOS == 1` (see Milestone 1's target_and_survey_variables.md).",
        "",
        f"- Counts: {class_imbalance['counts']}",
        f"- Percentages: {class_imbalance['percentages']}",
        f"- Imbalance ratio (majority:minority): {class_imbalance['imbalance_ratio']}:1",
        f"- Plot: `figures/{target_plot}`",
        "",
        "## 6. Correlation Analysis",
        "",
        "- Full numerical correlation matrix: `correlation_matrix.csv`",
        "- Variable pairs with |correlation| >= 0.7: `top_correlated_pairs.csv`"
        + (f" ({len(top_pairs)} found)" if not top_pairs.empty else " (none found)"),
        "- Numerical variables ranked by correlation with the target: `target_correlation.csv`",
        f"- Heatmap of key numerical variables: `figures/{heatmap_plot}`",
        "",
        "## 7. Outlier Analysis",
        "",
        "IQR-based outlier counts (1.5x IQR beyond Q1/Q3) are included per variable in "
        "`numerical_summary.csv` (`outlier_count` / `outlier_percentage` columns). Note the "
        "negative-sentinel-code caveat above — some flagged outliers are Not-applicable/Unknown "
        "codes rather than genuine extreme values.",
        "",
        "## 8. Distribution Plots",
        "",
        f"Plotted for {len(numerical_plots) + len(categorical_plots)} of "
        f"{len(KEY_NUMERICAL_VARIABLES) + len(KEY_CATEGORICAL_VARIABLES)} curated key variables "
        "(clinically meaningful vitals, demographics, and visit characteristics) plus the target. "
        "The remaining ~890 columns are administrative/free-text-coded fields already fully "
        "profiled in the summary CSVs above; plotting all of them individually was judged low "
        "value and was intentionally out of scope for this report.",
        "",
        "Numerical: " + ", ".join(f"`figures/{f}`" for f in numerical_plots),
        "",
        "Categorical: " + ", ".join(f"`figures/{f}`" for f in categorical_plots),
        "",
        "## Key Findings",
        "",
    ]

    if not target_corr.empty:
        top_variable = target_corr.iloc[0]
        lines.append(
            f"- `{top_variable['variable_name']}` has the strongest correlation with the target "
            f"({round(top_variable['correlation_with_target'], 3)})."
        )
        if top_variable["variable_name"] == "LOS":
            lines.append(
                "  `LOS` (length of hospital stay) is a leakage risk rather than a usable "
                "predictor: it is only populated for already-admitted visits (sentinel-coded "
                "otherwise) and is not known at the time an admission decision would be "
                "predicted. Flag for exclusion in Milestone 5/6."
            )

    if not top_pairs.empty:
        perfectly_correlated = top_pairs[top_pairs["correlation"].abs() >= 0.99]
        if not perfectly_correlated.empty:
            pair_list = ", ".join(
                f"`{row.variable_a}`/`{row.variable_b}`" for row in perfectly_correlated.itertuples()
            )
            lines.append(
                f"- Near-perfectly correlated pairs found: {pair_list}. These likely represent "
                "duplicate or recoded/derived versions of the same underlying item and are "
                "candidates for redundancy removal in Milestone 6 (Feature Selection)."
            )

    lines.append("")

    report_path = EDA_REPORTS_DIR / "eda_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 2 - Exploratory Data Analysis")
    EDA_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    config = load_config(DEFAULT_CONFIG_PATH)

    try:
        dataframe, metadata = load_dataset(config)
    except FileNotFoundError as error:
        logger.error("EDA aborted: %s", error)
        return

    numerical_columns, categorical_columns = split_columns_by_type(dataframe)
    logger.info(
        "Classified %d numerical and %d categorical columns", len(numerical_columns), len(categorical_columns)
    )

    missing_report = build_missing_value_report(dataframe)
    missing_report.to_csv(EDA_REPORTS_DIR / "missing_values_report.csv", index=False)
    missing_summary = summarize_missing_values(missing_report, dataframe.size)
    logger.info("Missing values: %.4f%% of all cells", missing_summary["overall_missing_percentage"])

    duplicate_summary = analyze_duplicates(dataframe)
    logger.info("Duplicate rows: %d", duplicate_summary["duplicate_row_count"])

    numerical_summary = build_numerical_summary(dataframe, numerical_columns)
    numerical_summary.to_csv(EDA_REPORTS_DIR / "numerical_summary.csv", index=False)
    logger.info("Wrote numerical_summary.csv (%d variables)", len(numerical_summary))

    categorical_summary = build_categorical_summary(dataframe, categorical_columns)
    categorical_summary.to_csv(EDA_REPORTS_DIR / "categorical_summary.csv", index=False)
    logger.info("Wrote categorical_summary.csv (%d variables)", len(categorical_summary))

    target = compute_derived_target(dataframe, config)
    class_imbalance = analyze_class_imbalance(target)
    logger.info("Class imbalance ratio: %s:1", class_imbalance["imbalance_ratio"])

    correlation_matrix = build_correlation_matrix(dataframe, numerical_columns)
    correlation_matrix.to_csv(EDA_REPORTS_DIR / "correlation_matrix.csv")

    top_pairs = top_correlated_pairs(correlation_matrix)
    top_pairs.to_csv(EDA_REPORTS_DIR / "top_correlated_pairs.csv", index=False)

    target_corr = target_correlation(dataframe, numerical_columns, target)
    target_corr.to_csv(EDA_REPORTS_DIR / "target_correlation.csv", index=False)

    numerical_plots = plot_numerical_distributions(dataframe, FIGURES_DIR)
    categorical_plots = plot_categorical_distributions(dataframe, FIGURES_DIR)
    target_plot = plot_target_distribution(target, FIGURES_DIR)
    heatmap_plot = plot_correlation_heatmap(correlation_matrix, KEY_NUMERICAL_VARIABLES, FIGURES_DIR)
    missing_heatmap_plot = plot_missing_value_heatmap(dataframe, missing_report, FIGURES_DIR)
    logger.info("Generated %d distribution plots", len(numerical_plots) + len(categorical_plots) + 3)

    write_eda_report(
        dataframe,
        numerical_columns,
        categorical_columns,
        missing_summary,
        duplicate_summary,
        class_imbalance,
        top_pairs,
        target_corr,
        numerical_plots,
        categorical_plots,
        target_plot,
        heatmap_plot,
        missing_heatmap_plot,
    )

    logger.info("Milestone 2 (Exploratory Data Analysis) completed successfully.")


if __name__ == "__main__":
    main()
