"""Variables excluded from the predictive feature set because they are
only known AFTER the admission decision (leakage), or because they are
hospital-facility-level questionnaire items rather than per-patient-visit
clinical data.

Identified by a systematic keyword sweep of all 913 original variable
labels (Milestone 1's data_dictionary.csv) cross-checked against the NCHS
codebook, not by memory alone.

DISPOSITION_BLOCK
    The 16 mutually-independent 0/1 "VISIT DISPOSITION" checkboxes
    (codebook item numbers 226-241). ADMITHOS/OBSHOS are consumed to
    derive the prediction target (see target.py) and must not also
    remain as features -- that would be using the answer to predict
    itself. The other 14 describe alternative outcomes of the same
    disposition decision and are equally unknown beforehand.

POST_ADMISSION_HOSPITAL_COURSE
    Fields that only exist, or are only populated, once a patient is
    already admitted and their hospital stay has begun or ended (which
    unit they went to, who admitted them, how long they stayed, their
    eventual hospital discharge diagnosis/status, boarding time). All of
    these are downstream consequences of the admission decision, not
    inputs to it.

FACILITY_LEVEL_QUESTIONNAIRE
    Items from the ED-level (not patient-level) facility questionnaire,
    weighted by EDWT rather than PATWT (ambulance diversion policy,
    staffing, bed-management practices). These describe the hospital,
    not the individual visit, and are out of scope for a per-visit
    admission-prediction model.
"""

DISPOSITION_BLOCK = {
    "NODISP", "NOFU", "RETRNED", "RETREFFU", "LWBS", "LBTC", "LEFTAMA",
    "DOA", "DIEDED", "TRANNH", "TRANPSYC", "TRANOTH",
    "ADMITHOS", "OBSHOS", "OBSDIS", "OTHDISP",
}

POST_ADMISSION_HOSPITAL_COURSE = {
    "ADMIT", "ADMTPHYS", "LOS",
    "HDDIAG1", "HDDIAG2", "HDDIAG3", "HDDIAG4", "HDDIAG5",
    "HDSTAT", "ADISP", "OBSSTAY", "BOARDED", "BOARDHOS", "STAY24",
}

FACILITY_LEVEL_QUESTIONNAIRE = {
    "OBSCLIN", "OBSSEP", "OBSPHYSED", "OBSHOSP", "OBSPHYSOT", "OBSPHYSUN",
    "BOARD", "AMBDIV", "TOTHRDIVR", "REGDIV", "ADMDIV", "BEDCZAR",
    "BEDDATA", "HLIST", "HLISTED", "EMEDRES",
}


def get_excluded_leakage_columns() -> set:
    return DISPOSITION_BLOCK | POST_ADMISSION_HOSPITAL_COURSE | FACILITY_LEVEL_QUESTIONNAIRE
