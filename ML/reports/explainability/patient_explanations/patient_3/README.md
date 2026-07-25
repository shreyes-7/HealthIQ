# Patient Explanation — patient_3_borderline

Generated: 2026-07-25T08:20:05.346689+00:00

**Selection reason**: Predicted probability closest to 0.5 -- the model's most uncertain case, most informative for understanding where evidence conflicts.

- Row index in validation split: 2213
- Predicted probability of admission: **0.5067**
- Base rate (population average) probability: 0.0002
- Predicted outcome: ADMITTED
- Actual outcome: ADMITTED
- Prediction was: CORRECT

## Variables That Increased Admission Risk

| Feature | Source Variable | Value | SHAP (margin) |
|---|---|---|---|
| `CONSULT__Yes` | `CONSULT` | 1.0 | +4.0032 |
| `NUMDIS` | `NUMDIS` | -0.4693230751077467 | +2.1099 |
| `TOTDIAG` | `TOTDIAG` | 2.0582446920196293 | +1.9052 |
| `COVIDTEST__Yes` | `COVIDTEST` | 1.0 | +0.7539 |
| `IVFLUIDS__Yes` | `IVFLUIDS` | 1.0 | +0.4104 |
| `PROC__1` | `PROC` | 1.0 | +0.3279 |
| `TEMPDF` | `TEMPDF` | -1.3030871701767737 | +0.2938 |
| `RESINT__Yes` | `RESINT` | 1.0 | +0.2490 |

## Variables That Decreased Admission Risk

| Feature | Source Variable | Value | SHAP (margin) |
|---|---|---|---|
| `DIAG1__frequency` | `DIAG1` | 0.008201836498172417 | -1.0536 |
| `AGE` | `AGE` | -1.3047399517378364 | -0.8237 |
| `LOV` | `LOV` | -0.08618478078664836 | -0.3933 |
| `FLUTEST__Yes` | `FLUTEST` | 1.0 | -0.3516 |
| `DIAG2__frequency` | `DIAG2` | 0.005349023803155924 | -0.2463 |
| `ARREMS__1` | `ARREMS` | 0.0 | -0.1846 |
| `RX2CAT1__frequency` | `RX2CAT1` | 0.42881340821966657 | -0.1664 |
| `WAITTIME` | `WAITTIME` | 0.12012913213919993 | -0.1661 |

## Visualizations

- `waterfall_plot.png` — step-by-step from base rate to final prediction
- `force_plot.png` — same information, compact horizontal layout
- `decision_plot.png` — cumulative path of the prediction across top features