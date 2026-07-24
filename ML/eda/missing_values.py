"""Missing value analysis. Read-only: no values are imputed or removed."""

import pandas as pd


def build_missing_value_report(dataframe: pd.DataFrame) -> pd.DataFrame:
    missing_counts = dataframe.isna().sum()
    missing_percentage = (missing_counts / len(dataframe) * 100).round(2)

    report = pd.DataFrame(
        {
            "variable_name": dataframe.columns,
            "missing_count": missing_counts.values,
            "missing_percentage": missing_percentage.values,
        }
    )
    return report.sort_values("missing_percentage", ascending=False).reset_index(drop=True)


def summarize_missing_values(missing_report: pd.DataFrame, total_cells: int) -> dict:
    total_missing_cells = int(missing_report["missing_count"].sum())
    fully_missing_columns = missing_report.loc[
        missing_report["missing_percentage"] == 100.0, "variable_name"
    ].tolist()

    return {
        "total_cells": total_cells,
        "total_missing_cells": total_missing_cells,
        "overall_missing_percentage": round(total_missing_cells / total_cells * 100, 4),
        "columns_with_no_missing_values": int((missing_report["missing_percentage"] == 0).sum()),
        "columns_over_50_percent_missing": int((missing_report["missing_percentage"] > 50).sum()),
        "fully_missing_columns": fully_missing_columns,
    }
