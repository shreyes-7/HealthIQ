"""The curated patient-record request schema.

`ML.pipeline.preprocessing_pipeline.PreprocessingPipeline.transform()` was
trained against the full ~900-column raw NHAMCS row, and several of its
cleaning steps index a fixed, previously-learned column list without an
existence check -- a column missing entirely (not just null) raises a
KeyError. Requiring an API client to supply ~900 raw survey fields would
violate PROJECT_CONTEXT.md's "simple, require minimal user effort"
requirement for the patient prediction interface, so this schema exposes
only the clinically meaningful fields a physician would realistically have
at hand (demographics, vitals, triage, arrival, and the workup fields the
Sprint 3 SHAP analysis found most influential). Every field the client
omits is left null in the assembled raw record
(`Backend.app.services.patient_record_assembler`) and filled by the same
fitted median / "Missing"-category imputation the pipeline already applies
to any other missing value -- no separate imputation logic is introduced
here.

Coded fields (sex, race_ethnicity, triage_level) are passed through as raw
NHAMCS codebook integers rather than as strings -- translating them to the
human-readable labels below is presentation logic (dropdown option text),
which belongs in the Frontend, not in this request contract. The wire
format doesn't need to change for that; only the frontend form needs the
label text. Value labels confirmed against
`Data/documents/technical Documentation.pdf` (via `pdftotext`, not
guessed) in Sprint 5:

    SEX (sex):            1 = Female, 2 = Male
    RACERETH (race_ethnicity): 1 = Non-Hispanic White, 2 = Non-Hispanic Black,
                                3 = Hispanic, 4 = Non-Hispanic Other
    IMMEDR (triage_level): 1 = Immediate, 2 = Emergent, 3 = Urgent,
                            4 = Semi-urgent, 5 = Non-urgent
                            (0 = visit had no triage / 7 = ESA does not
                            conduct nursing triage -- not accepted here,
                            since this schema only models the 5-point scale)

`arrived_by_ambulance` (ARREMS: 1=Yes, 2=No) and `consult_requested`
(CONSULT: 0=No, 1=Yes) were already confidently mapped to booleans in
Sprint 4 and are now independently confirmed by the same codebook check.
"""

from typing import Literal

from pydantic import BaseModel, Field


class PatientRecordRequest(BaseModel):
    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "age": 67,
                    "sex": 2,
                    "race_ethnicity": 1,
                    "pulse": 88,
                    "temperature_fahrenheit": 98.6,
                    "respiratory_rate": 18,
                    "systolic_bp": 130,
                    "diastolic_bp": 80,
                    "pulse_oximetry_percent": 97,
                    "triage_level": 2,
                    "arrived_by_ambulance": True,
                    "wait_time_minutes": 15,
                    "length_of_visit_minutes": 120,
                    "num_discharge_diagnoses": 3,
                    "total_diagnoses": 4,
                    "consult_requested": True,
                    "primary_diagnosis_code": "R079",
                    "num_medications": 2,
                    "num_medications_given": 1,
                }
            ]
        },
    }

    # Demographics
    age: int = Field(..., ge=0, le=120, description="Patient age in years.")
    sex: Literal[1, 2] = Field(..., description="NHAMCS SEX code: 1 = Female, 2 = Male.")
    race_ethnicity: Literal[1, 2, 3, 4] | None = Field(
        None,
        description=(
            "NHAMCS RACERETH code: 1 = Non-Hispanic White, 2 = Non-Hispanic Black, "
            "3 = Hispanic, 4 = Non-Hispanic Other."
        ),
    )

    # Vitals
    pulse: int = Field(..., ge=0, le=300, description="Pulse, beats per minute.")
    temperature_fahrenheit: float = Field(..., ge=70.0, le=115.0, description="Body temperature, degrees Fahrenheit.")
    respiratory_rate: int = Field(..., ge=0, le=100, description="Respirations per minute.")
    systolic_bp: int = Field(..., ge=0, le=300, description="Systolic blood pressure, mmHg.")
    diastolic_bp: int = Field(..., ge=0, le=200, description="Diastolic blood pressure, mmHg.")
    pulse_oximetry_percent: int | None = Field(None, ge=0, le=100, description="Pulse oximetry, percent oxygen saturation.")

    # Visit / triage / arrival
    triage_level: int = Field(
        ...,
        ge=1,
        le=5,
        description="NHAMCS IMMEDR triage acuity: 1 = Immediate, 2 = Emergent, 3 = Urgent, 4 = Semi-urgent, 5 = Non-urgent.",
    )
    arrived_by_ambulance: bool = Field(..., description="Whether the patient arrived by ambulance.")
    wait_time_minutes: int | None = Field(None, ge=0, description="Minutes from arrival to being seen by a provider.")
    length_of_visit_minutes: int | None = Field(None, ge=0, description="Total ED length of visit, in minutes.")

    # Workup (available once assessment is underway; optional at request time)
    num_discharge_diagnoses: int | None = Field(None, ge=0, le=20, description="Number of discharge diagnoses recorded.")
    total_diagnoses: int | None = Field(None, ge=0, le=20, description="Total number of diagnoses recorded for the visit.")
    consult_requested: bool | None = Field(None, description="Whether a specialist consultation was requested.")
    primary_diagnosis_code: str | None = Field(
        None, max_length=10, description="Primary diagnosis, ICD-10-CM code (NHAMCS DIAG1), e.g. 'R079'."
    )
    num_medications: int | None = Field(None, ge=0, le=50, description="Number of medications recorded for the visit.")
    num_medications_given: int | None = Field(None, ge=0, le=50, description="Number of medications given in the ED.")
