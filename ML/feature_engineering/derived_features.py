"""Creates interpretable, clinically-established derived features from
existing vitals.

Stateless: pure arithmetic/threshold rules applied to already-cleaned
columns (imputed, sentinel-free as of Milestone 3), so the exact same
values are produced whether called during fit or transform -- no fitting
required, and safe to reapply to any new data.

Each derived feature is a well-established marker in emergency medicine
literature, chosen for interpretability over speculative combinations:

- SHOCK_INDEX (pulse / systolic BP): a widely-used bedside severity
  marker; normal is roughly 0.5-0.7, values above ~0.9 are associated
  with hemodynamic instability and higher admission risk.
- PULSE_PRESSURE (systolic - diastolic BP): an abnormally narrow pulse
  pressure can indicate reduced cardiac output.
- FEVER_FLAG, TACHYCARDIC_FLAG, HYPOTENSIVE_FLAG: standard clinical
  threshold flags, more directly interpretable to a clinician than the
  raw scaled vital-sign value alone.
- AGE_GROUP: standard age bands used throughout ED research (infant,
  child, adolescent, adult, older adult), capturing non-linear age
  effects that a single scaled AGE value cannot.
"""

import pandas as pd

DERIVED_CONTINUOUS_COLUMNS = ["SHOCK_INDEX", "PULSE_PRESSURE"]
DERIVED_CATEGORICAL_COLUMNS = ["FEVER_FLAG", "TACHYCARDIC_FLAG", "HYPOTENSIVE_FLAG", "AGE_GROUP"]

FEVER_THRESHOLD_FAHRENHEIT = 100.4
TACHYCARDIA_THRESHOLD_BPM = 100
HYPOTENSION_THRESHOLD_MMHG = 90

AGE_GROUP_BIN_EDGES = [-1, 1, 12, 17, 64, 200]
AGE_GROUP_LABELS = ["infant_0_1", "child_2_12", "adolescent_13_17", "adult_18_64", "older_adult_65_plus"]


def _flag(condition: pd.Series) -> pd.Series:
    return condition.map({True: "Yes", False: "No"}).astype("category")


def add_derived_clinical_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    enriched = dataframe.copy()

    # BPSYS == 0 is a documented, valid (if rare) NHAMCS code, not a
    # sentinel -- guard the division rather than producing inf/NaN.
    safe_systolic_bp = enriched["BPSYS"].where(enriched["BPSYS"] > 0, 1)
    enriched["SHOCK_INDEX"] = (enriched["PULSE"] / safe_systolic_bp).astype("float64")
    enriched["PULSE_PRESSURE"] = (enriched["BPSYS"] - enriched["BPDIAS"]).astype("float64")

    enriched["FEVER_FLAG"] = _flag(enriched["TEMPF"] >= FEVER_THRESHOLD_FAHRENHEIT)
    enriched["TACHYCARDIC_FLAG"] = _flag(enriched["PULSE"] > TACHYCARDIA_THRESHOLD_BPM)
    enriched["HYPOTENSIVE_FLAG"] = _flag(enriched["BPSYS"] < HYPOTENSION_THRESHOLD_MMHG)

    enriched["AGE_GROUP"] = pd.cut(
        enriched["AGE"], bins=AGE_GROUP_BIN_EDGES, labels=AGE_GROUP_LABELS
    ).astype("category")

    return enriched
