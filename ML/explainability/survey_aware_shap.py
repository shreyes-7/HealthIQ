"""Survey-Aware Deep Dive, Part 2: does survey weighting change what the
model's explanations say, not just its raw performance?

Sprint 3's entire SHAP analysis ran on the standard (unweighted) model
only -- this was flagged as open "Future Work" in the Sprint 3 research
report. This module computes SHAP values for the survey-weighted
LightGBM (same TreeExplainer approach as Sprint 3) and compares them
against the already-computed unweighted SHAP values.
"""

from scipy.stats import spearmanr

from ML.explainability.shap_utils import mean_absolute_shap_by_source_variable


def compare_importance_rankings(
    unweighted_shap_values, weighted_shap_values, feature_names: list[str], top_n: int = 20
) -> dict:
    unweighted_ranking = mean_absolute_shap_by_source_variable(unweighted_shap_values, feature_names)
    weighted_ranking = mean_absolute_shap_by_source_variable(weighted_shap_values, feature_names)

    common_variables = unweighted_ranking.index.intersection(weighted_ranking.index)
    rank_correlation, p_value = spearmanr(
        unweighted_ranking.loc[common_variables].rank(ascending=False),
        weighted_ranking.loc[common_variables].rank(ascending=False),
    )

    unweighted_top_n = set(unweighted_ranking.head(top_n).index)
    weighted_top_n = set(weighted_ranking.head(top_n).index)
    overlap = unweighted_top_n & weighted_top_n

    return {
        "spearman_rank_correlation": float(rank_correlation),
        "spearman_p_value": float(p_value),
        "top_n": top_n,
        "top_n_overlap_count": len(overlap),
        "top_n_overlap_variables": sorted(overlap),
        "only_in_unweighted_top_n": sorted(unweighted_top_n - weighted_top_n),
        "only_in_weighted_top_n": sorted(weighted_top_n - unweighted_top_n),
        "unweighted_ranking": unweighted_ranking.head(top_n).to_dict(),
        "weighted_ranking": weighted_ranking.head(top_n).to_dict(),
    }
