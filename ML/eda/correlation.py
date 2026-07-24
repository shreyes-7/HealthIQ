"""Correlation analysis among numerical variables and against the target."""

import pandas as pd

HIGH_CORRELATION_THRESHOLD = 0.7


def build_correlation_matrix(dataframe: pd.DataFrame, numerical_columns: list[str]) -> pd.DataFrame:
    return dataframe[numerical_columns].corr()


def top_correlated_pairs(
    correlation_matrix: pd.DataFrame, threshold: float = HIGH_CORRELATION_THRESHOLD, top_n: int = 30
) -> pd.DataFrame:
    columns = correlation_matrix.columns
    pairs = []

    for i, column_a in enumerate(columns):
        for column_b in columns[i + 1 :]:
            correlation_value = correlation_matrix.loc[column_a, column_b]
            if pd.notna(correlation_value) and abs(correlation_value) >= threshold:
                pairs.append(
                    {"variable_a": column_a, "variable_b": column_b, "correlation": round(correlation_value, 3)}
                )

    pairs_df = pd.DataFrame(pairs)
    if pairs_df.empty:
        return pairs_df

    sort_order = pairs_df["correlation"].abs().sort_values(ascending=False).index
    return pairs_df.loc[sort_order].head(top_n).reset_index(drop=True)


def target_correlation(
    dataframe: pd.DataFrame, numerical_columns: list[str], target: pd.Series, top_n: int = 20
) -> pd.DataFrame:
    correlations = {column: dataframe[column].corr(target) for column in numerical_columns}
    correlation_series = pd.Series(correlations, name="correlation_with_target").dropna()

    sort_order = correlation_series.abs().sort_values(ascending=False).index
    top_correlations = correlation_series.loc[sort_order].head(top_n)

    return top_correlations.reset_index().rename(columns={"index": "variable_name"})
