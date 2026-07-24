"""Documented, per-variable cleaning roles for the NHAMCS dataset.

The EDA (Milestone 2) numerical/categorical split used a generic
cardinality heuristic (nunique > 20 => numerical). That heuristic is too
coarse for cleaning decisions: several "numerical" columns are actually
identifiers or nominal classification codes, not continuous measurements,
and several have codebook-documented special values that a generic rule
would not know about. The roles below were confirmed against the NCHS
technical documentation codebook (item-by-item), not guessed.

SURVEY_VARIABLES
    Never modified in any way (no sentinel conversion, no imputation, no
    dtype change) per the explicit requirement to preserve survey design
    variables for the survey-aware learning workflow.

IDENTIFIER_VARIABLES
    Hospital/patient record identifiers. Passed through unchanged; never
    treated as a measurement or a category to impute.

CONTINUOUS_NUMERICAL_VARIABLES
    Genuine continuous measurements. Sentinel codes are converted to NaN
    and the result is median-imputed.

CONDITIONAL_NUMERICAL_VARIABLES
    Continuous fields that are only defined for a subset of visits (e.g.
    LOS only exists for admitted patients; codebook code -7 = "Not
    applicable"). Sentinel codes are converted to NaN but the column is
    deliberately NOT imputed: filling a population median into a field
    that does not conceptually apply to most rows would fabricate
    information rather than clean it. Left as NaN for a later, dedicated
    feature-engineering step that models the condition explicitly.

NOMINAL_CODE_VARIABLES
    Numerically-typed but nominal classification codes (NHAMCS "Reason for
    Visit" codes). A median of a classification code is meaningless, so
    these are treated as high-cardinality categorical variables, not
    continuous ones.

Everything else in the dataset is treated as generic categorical.
"""

SURVEY_VARIABLES = {"PATWT", "EDWT", "CSTRATM", "CPSUM"}

IDENTIFIER_VARIABLES = {"HOSPCODE", "PATCODE"}

CONTINUOUS_NUMERICAL_VARIABLES = {
    "WAITTIME", "LOV", "AGE",
    "TEMPF", "PULSE", "RESPR", "BPSYS", "BPDIAS", "POPCT",
    "TEMPDF", "PULSED", "RESPRD", "BPSYSD", "BPDIASD",
    "TOTDIAG", "NUMGIV", "NUMDIS", "NUMMED",
}

CONDITIONAL_NUMERICAL_VARIABLES = {"AGEDAYS", "LOS", "OBSSTAY", "BOARDED"}

# Consumed by ML.feature_engineering.target.derive_target() to build the
# prediction target. Must never be dropped by variance-based cleaning
# steps (constant-column removal): OBSHOS is positive in only ~1% of
# visits, so it can easily be locally constant within a small sample
# (a test slice, or a future stratified fold) even though it is never
# constant across the full population -- dropping it during fit would
# make target derivation crash on any later transform() call.
TARGET_SOURCE_VARIABLES = {"ADMITHOS", "OBSHOS"}

NOMINAL_CODE_VARIABLES = {
    "RFV1", "RFV2", "RFV3", "RFV4", "RFV5",
    "RFV13D", "RFV23D", "RFV33D", "RFV43D", "RFV53D",
}

# Codebook-documented implied-decimal variables: the raw stored integer
# must be divided by 10 to get the real-world value.
# TEMPF/TEMPDF: "implied decimal between the third and fourth digits"
# RFV1-5: "10050-89990 = 1005.0-8999.0"
IMPLIED_DECIMAL_VARIABLES = {"TEMPF", "TEMPDF", "RFV1", "RFV2", "RFV3", "RFV4", "RFV5"}

# Codebook-documented non-numeric annotation codes that must become NaN
# rather than be read as a literal measurement (e.g. PULSE == 998 means
# "measured by Doppler", not a heart rate of 998).
NON_NUMERIC_ANNOTATION_CODES = {
    "PULSE": {998},
    "PULSED": {998},
    "BPDIAS": {998},
    "BPDIASD": {998},
}

# NHAMCS-wide sentinel codes (confirmed via codebook + full-dataset scan):
# -9 = Blank, -8 = Data not available / Unknown, -7 = Not applicable.
SENTINEL_CODES = {-7, -8, -9}


def get_all_special_role_columns() -> set:
    """Columns that receive dedicated handling rather than the generic
    categorical pathway."""
    return (
        SURVEY_VARIABLES
        | IDENTIFIER_VARIABLES
        | CONTINUOUS_NUMERICAL_VARIABLES
        | CONDITIONAL_NUMERICAL_VARIABLES
        | NOMINAL_CODE_VARIABLES
    )
