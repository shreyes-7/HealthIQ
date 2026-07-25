# Patient Explanation — patient_1_confident_admission

Generated: 2026-07-25T08:20:00.689781+00:00

**Selection reason**: Highest-confidence correctly-predicted admission -- the clearest positive case.

- Row index in validation split: 1809
- Predicted probability of admission: **0.9999**
- Base rate (population average) probability: 0.0002
- Predicted outcome: ADMITTED
- Actual outcome: ADMITTED
- Prediction was: CORRECT

## Variables That Increased Admission Risk

| Feature | Source Variable | Value | SHAP (margin) |
|---|---|---|---|
| `CONSULT__Yes` | `CONSULT` | 1.0 | +3.1893 |
| `NUMDIS` | `NUMDIS` | -0.4693230751077467 | +2.2389 |
| `TOTDIAG` | `TOTDIAG` | 2.912276654179341 | +2.0203 |
| `BLOODCX__Yes` | `BLOODCX` | 1.0 | +0.9944 |
| `COVIDTEST__Yes` | `COVIDTEST` | 1.0 | +0.6552 |
| `IVFLUIDS__Yes` | `IVFLUIDS` | 1.0 | +0.4687 |
| `MED3__frequency` | `MED3` | 0.000445751983596327 | +0.4606 |
| `CKD__Yes` | `CKD` | 1.0 | +0.4134 |

## Variables That Decreased Admission Risk

| Feature | Source Variable | Value | SHAP (margin) |
|---|---|---|---|
| `RACEUN__2` | `RACEUN` | 1.0 | -0.2744 |
| `ELECTROL__Yes` | `ELECTROL` | 1.0 | -0.2469 |
| `FLUTEST__Yes` | `FLUTEST` | 1.0 | -0.1361 |
| `IMBED__2` | `IMBED` | 1.0 | -0.1221 |
| `BPDIAS` | `BPDIAS` | 1.5647386671466177 | -0.1212 |
| `TEMPDF` | `TEMPDF` | 2.0054556898798763 | -0.1131 |
| `BPSYSD` | `BPSYSD` | 1.2001381514759977 | -0.1003 |
| `RX1CAT2__frequency` | `RX1CAT2` | 0.01239190514397789 | -0.0857 |

## Visualizations

- `waterfall_plot.png` — step-by-step from base rate to final prediction
- `force_plot.png` — same information, compact horizontal layout
- `decision_plot.png` — cumulative path of the prediction across top features