"""Generates distribution plots for a curated set of key variables.

Producing an individual plot for all 913 columns would be impractical and
low-value: most columns are sparse administrative fields, free-text-coded
identifiers, or one-hot medication flags already covered numerically by
numerical_summary.csv / categorical_summary.csv. This module plots a
curated subset of clinically meaningful variables plus the prediction
target so the report stays readable, while the full statistical profile of
every variable remains available in the summary tables.
"""

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)

KEY_NUMERICAL_VARIABLES = [
    "AGE", "WAITTIME", "LOV", "TEMPF", "PULSE", "RESPR", "BPSYS", "BPDIAS", "POPCT", "BOARDED",
]
KEY_CATEGORICAL_VARIABLES = [
    "SEX", "AGER", "RACER", "ETHUN", "ARREMS", "PAYTYPER", "IMMEDR", "PAINSCALE", "VDAYR", "VMONTH", "STAY24",
]


def plot_numerical_distributions(dataframe: pd.DataFrame, output_dir: Path) -> list[str]:
    generated_files = []
    for column in KEY_NUMERICAL_VARIABLES:
        if column not in dataframe.columns:
            logger.warning("Skipping numerical plot for missing column: %s", column)
            continue

        figure, axis = plt.subplots(figsize=(6, 4))
        dataframe[column].dropna().plot(kind="hist", bins=30, ax=axis)
        axis.set_title(f"Distribution of {column}")
        axis.set_xlabel(column)

        file_path = output_dir / f"{column.lower()}_histogram.png"
        figure.tight_layout()
        figure.savefig(file_path)
        plt.close(figure)
        generated_files.append(file_path.name)

    return generated_files


def plot_categorical_distributions(dataframe: pd.DataFrame, output_dir: Path) -> list[str]:
    generated_files = []
    for column in KEY_CATEGORICAL_VARIABLES:
        if column not in dataframe.columns:
            logger.warning("Skipping categorical plot for missing column: %s", column)
            continue

        figure, axis = plt.subplots(figsize=(6, 4))
        dataframe[column].value_counts(dropna=False).sort_index().plot(kind="bar", ax=axis)
        axis.set_title(f"Distribution of {column}")
        axis.set_xlabel(column)
        axis.set_ylabel("Count")

        file_path = output_dir / f"{column.lower()}_bar.png"
        figure.tight_layout()
        figure.savefig(file_path)
        plt.close(figure)
        generated_files.append(file_path.name)

    return generated_files


def plot_target_distribution(target: pd.Series, output_dir: Path) -> str:
    figure, axis = plt.subplots(figsize=(5, 4))
    target.value_counts().sort_index().plot(kind="bar", ax=axis, color=["#4C72B0", "#C44E52"])
    axis.set_title(f"Class Distribution: {target.name}")
    axis.set_xlabel(f"{target.name} (0 = No, 1 = Yes)")
    axis.set_ylabel("Count")

    file_path = output_dir / "target_class_distribution_bar.png"
    figure.tight_layout()
    figure.savefig(file_path)
    plt.close(figure)
    return file_path.name


def plot_missing_value_heatmap(
    dataframe: pd.DataFrame, missing_report: pd.DataFrame, output_dir: Path, top_n: int = 30
) -> str:
    """Heatmap of missingness for the top-N columns with the highest missing percentage.

    Plotting all 913 columns would be unreadable; the top-N view highlights whether
    missingness is scattered randomly or clustered by row (e.g. entire visit records
    skipping a block of related items).
    """
    top_missing_columns = missing_report.head(top_n)["variable_name"].tolist()
    missingness = dataframe[top_missing_columns].isna()

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.imshow(missingness.values.T, aspect="auto", cmap="Greys", interpolation="none")
    axis.set_yticks(range(len(top_missing_columns)))
    axis.set_yticklabels(top_missing_columns, fontsize=7)
    axis.set_xlabel("Row index")
    axis.set_title(f"Missing Value Heatmap (top {top_n} columns by missing %)")

    file_path = output_dir / "missing_value_heatmap.png"
    figure.tight_layout()
    figure.savefig(file_path)
    plt.close(figure)
    return file_path.name


def plot_correlation_heatmap(correlation_matrix: pd.DataFrame, columns: list[str], output_dir: Path) -> str:
    subset_columns = [column for column in columns if column in correlation_matrix.columns]
    subset = correlation_matrix.loc[subset_columns, subset_columns]

    figure, axis = plt.subplots(figsize=(8, 7))
    image = axis.imshow(subset.values, vmin=-1, vmax=1, cmap="coolwarm")
    axis.set_xticks(range(len(subset_columns)))
    axis.set_xticklabels(subset_columns, rotation=90)
    axis.set_yticks(range(len(subset_columns)))
    axis.set_yticklabels(subset_columns)
    figure.colorbar(image, ax=axis)
    axis.set_title("Correlation Heatmap (key numerical variables)")

    file_path = output_dir / "correlation_heatmap.png"
    figure.tight_layout()
    figure.savefig(file_path)
    plt.close(figure)
    return file_path.name
