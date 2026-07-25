# Patient Explanation — patient_2_confident_discharge

Generated: 2026-07-25T08:20:02.876175+00:00

**Selection reason**: Lowest-confidence-of-admission correctly-predicted discharge -- the clearest negative case.

- Row index in validation split: 1219
- Predicted probability of admission: **0.0000**
- Base rate (population average) probability: 0.0002
- Predicted outcome: NOT ADMITTED
- Actual outcome: NOT ADMITTED
- Prediction was: CORRECT

## Variables That Increased Admission Risk

| Feature | Source Variable | Value | SHAP (margin) |
|---|---|---|---|
| `DIAG1__frequency` | `DIAG1` | 0.000891503967192654 | +0.4637 |
| `PROC__1` | `PROC` | 1.0 | +0.2107 |
| `PAINSCALE__9` | `PAINSCALE` | 1.0 | +0.1431 |
| `RFV23D__frequency` | `RFV23D` | 0.3633770170277258 | +0.0832 |
| `TOTPROC__1` | `TOTPROC` | 1.0 | +0.0606 |
| `ANYIMAGE__No` | `ANYIMAGE` | 0.0 | +0.0517 |
| `OTHPROV__Yes` | `OTHPROV` | 1.0 | +0.0485 |
| `INJURY72__1` | `INJURY72` | 1.0 | +0.0452 |

## Variables That Decreased Admission Risk

| Feature | Source Variable | Value | SHAP (margin) |
|---|---|---|---|
| `NUMDIS` | `NUMDIS` | -0.026825224096265296 | -1.2869 |
| `CASTSPLINT__Yes` | `CASTSPLINT` | 1.0 | -0.5737 |
| `TOTDIAG` | `TOTDIAG` | -0.7885285151794068 | -0.5713 |
| `CONSULT__Yes` | `CONSULT` | 0.0 | -0.5482 |
| `LOV` | `LOV` | -0.29050627390964623 | -0.4307 |
| `COVIDTEST__Yes` | `COVIDTEST` | 0.0 | -0.3511 |
| `IMMEDR__4` | `IMMEDR` | 1.0 | -0.3374 |
| `EDPRIM__4` | `EDPRIM` | 1.0 | -0.2821 |

## Visualizations

- `waterfall_plot.png` — step-by-step from base rate to final prediction
- `force_plot.png` — same information, compact horizontal layout
- `decision_plot.png` — cumulative path of the prediction across top features