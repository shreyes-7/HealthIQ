# Survey-Aware Deep Dive: Consolidated Summary

Generated: 2026-07-25T12:45:55.675189+00:00

This project's stated primary research contribution (`Docs/PROJECT_CONTEXT.md` §44) is survey-aware prediction: using NHAMCS's `PATWT` sample weights so the model reflects the U.S. population the survey is designed to estimate, rather than only the raw sample. Sprint 2 took a first pass at this with Logistic Regression only, never connected to the production model, SHAP explainability, or fairness. This deep dive closes that gap by running the full comparison — performance, explanations, and fairness — on the actual production LightGBM model.

Three questions, three reports:

| Question | Report | Headline Finding |
|---|---|---|
| Does survey weighting change raw performance? | [weighted_vs_unweighted_lightgbm.md](weighted_vs_unweighted_lightgbm.md) | Validation ROC-AUC -0.0022, test ROC-AUC -0.0030 — small, expected decreases, far smaller than Sprint 2's Logistic Regression gap |
| Does survey weighting change what the model bases its explanations on? | [shap_comparison_report.md](shap_comparison_report.md) | Spearman rank correlation 0.9725, 18/20 top-feature overlap — reasoning is stable; only 47/2404 (1.96%) predictions flip, concentrated near the decision boundary |
| Does survey weighting change fairness across race/ethnicity? | [fairness_audit_report.md](fairness_audit_report.md) | 3/4 disparity gaps narrow (selection_rate, true_positive_rate, false_positive_rate); 1/4 widen (roc_auc) |

## Synthesis

The three findings fit together into a coherent story. Survey weighting trades a small amount of raw in-sample discrimination for population representativeness — expected, since `PATWT` deliberately up-weights underrepresented sampling strata. That trade does **not** destabilize the model's clinical reasoning: the same features drive predictions in essentially the same order, and the vast majority of predictions do not change at all. Where predictions do change, they concentrate almost entirely on cases the model was already uncertain about (near the 0.5 decision boundary) — exactly where a small shift in training weights would be expected to matter, and exactly where a clinician would want a second look anyway.

Most importantly for this project's research framing: the small performance cost of survey weighting buys a real, measurable improvement in equity — 3 of 4 fairness metrics improve for race/ethnicity subgroups on the validation split. This is the strongest evidence in the project so far that survey-aware learning is not just methodologically correct but practically worthwhile: it is not merely a more statistically rigorous way to fit the same model, it changes the model's behavior in a direction the project should prefer.

## Caveats

- All three analyses use a single validation split with no bootstrap confidence intervals around the reported gaps or deltas — treat magnitudes as indicative, not statistically certified.
- The fairness audit covers one protected attribute (`RACERETH`). Sex (`SEX`) and age group are natural next candidates given they are also present in the feature set.
- The per-group ROC-AUC gap widens slightly even though threshold-dependent fairness metrics narrow — see the caveat in `fairness_audit_report.md` for why these can diverge.

## Artifacts

- `weighted_vs_unweighted_lightgbm.md` / `.json` — performance comparison
- `shap_comparison_report.md` / `.json` — explanation comparison and decision-flip analysis
- `fairness_audit_report.md` / `.json` — fairness audit across RACERETH
- `figures/` — supporting visualizations for all three
- `ML/saved_models/model_survey_weighted.pkl` — the survey-weighted model artifact itself