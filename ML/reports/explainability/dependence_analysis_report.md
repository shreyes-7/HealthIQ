# Dependence Analysis Report

Generated: 2026-07-25T08:23:12.073797+00:00

Dependence plots for the top 3 features by global importance, plus additional important **continuous** variables (prioritized over one-hot dummies, which only show two point clouds rather than a traceable curve). Each plot is auto-colored by SHAP's chosen interaction feature.

Top 3: ['NUMDIS', 'CONSULT__Yes', 'TOTDIAG']
Additional: ['DIAG1__frequency', 'LOV', 'AGE', 'DIAG2__frequency', 'DRUGID2__frequency']

## Observations

- `NUMDIS`: value range [-0.47, 11.92], Pearson correlation between raw value and SHAP contribution: -0.471 (nonlinear or threshold-like relationship — see plot)
- `CONSULT__Yes`: value range [0.00, 1.00], Pearson correlation between raw value and SHAP contribution: 0.978 (roughly monotonic/linear)
- `TOTDIAG`: value range [-1.07, 4.05], Pearson correlation between raw value and SHAP contribution: 0.950 (roughly monotonic/linear)
- `DIAG1__frequency`: value range [0.00, 0.03], Pearson correlation between raw value and SHAP contribution: -0.757 (roughly monotonic/linear)
- `LOV`: value range [-0.72, 13.14], Pearson correlation between raw value and SHAP contribution: 0.744 (roughly monotonic/linear)
- `AGE`: value range [-1.63, 2.14], Pearson correlation between raw value and SHAP contribution: 0.776 (roughly monotonic/linear)
- `DIAG2__frequency`: value range [0.00, 0.47], Pearson correlation between raw value and SHAP contribution: -0.614 (roughly monotonic/linear)
- `DRUGID2__frequency`: value range [0.00, 0.43], Pearson correlation between raw value and SHAP contribution: -0.501 (nonlinear or threshold-like relationship — see plot)

See `dependence_plots/*.png` for the actual shape of each relationship — a single correlation number above cannot distinguish a threshold effect from a smooth nonlinear one; the plots are the primary artifact here, this table is a navigation aid.