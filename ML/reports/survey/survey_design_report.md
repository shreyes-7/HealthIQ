# Survey Design Report

Generated: 2026-07-24T17:43:07.136301+00:00

Survey weight (`PATWT`) values verified untouched (subset-of-raw check) across all splits: **True**.

## Design Diagnostics per Split

| Split | Rows | Unique Strata | Unique PSUs | Weight Sum | Weight CV | Approx. Kish Design Effect |
|---|---|---|---|---|---|---|
| train | 11217 | 8 | 122 | 107955414.8 | 0.998 | 1.995 |
| validation | 2404 | 8 | 121 | 23314978.9 | 1.020 | 2.041 |
| test | 2404 | 8 | 122 | 24127352.9 | 1.001 | 2.002 |

The approximate Kish design effect (`1 + CV(weight)^2`) is a simplified, weight-only proxy (Kish, 1965) -- not a full variance-based design effect, which needs an actual outcome and a proper survey-design estimator. It is provided so Phase 2 knows roughly how much the unequal weighting alone inflates variance, before adding clustering/stratification effects.

## PSU Overlap Across Splits

**Methodology caveat:** Milestone 7's train/validation/test split is stratified by the prediction target (a simple, standard choice for the traditional ML workflow) — it does NOT preserve PSU (cluster) boundaries. The same PSU can appear in more than one split:

- `train_and_validation`: {'shared_psu_count': 121, 'train_psu_count': 122, 'validation_psu_count': 121}
- `train_and_test`: {'shared_psu_count': 122, 'train_psu_count': 122, 'test_psu_count': 122}
- `validation_and_test`: {'shared_psu_count': 121, 'validation_psu_count': 121, 'test_psu_count': 122}

This is standard and acceptable for evaluating the traditional (non-survey-weighted) ML workflow. For rigorous **design-based** variance estimation in the survey-aware workflow (Phase 2's comparison objective), PSU overlap between the fitting and evaluation sets is a known limitation -- if precise design-based standard errors are required, Phase 2 should consider a PSU-level (cluster-preserving) split as an alternative, evaluated against this target-stratified split rather than assumed superior, since it would trade off exact class balance across splits.

## Scope

This report verifies preservation and provides diagnostics only. Actual survey-weighted model fitting (`svyset`-equivalent estimation, comparison against the traditional workflow) is Phase 2's Survey-Aware Machine Learning objective (PROJECT_CONTEXT.md Section 44), not a data engineering task.
