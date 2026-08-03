import pytest
from pydantic import ValidationError

from Backend.app.schemas.patient import PatientRecordRequest

VALID_PAYLOAD = {
    "age": 67,
    "sex": 2,
    "pulse": 88,
    "temperature_fahrenheit": 98.6,
    "respiratory_rate": 18,
    "systolic_bp": 130,
    "diastolic_bp": 80,
    "triage_level": 2,
    "arrived_by_ambulance": True,
}


def test_accepts_only_required_fields():
    record = PatientRecordRequest(**VALID_PAYLOAD)
    assert record.age == 67
    assert record.race_ethnicity is None


def test_accepts_full_payload():
    payload = {
        **VALID_PAYLOAD,
        "race_ethnicity": 1,
        "pulse_oximetry_percent": 97,
        "wait_time_minutes": 15,
        "length_of_visit_minutes": 120,
        "num_discharge_diagnoses": 3,
        "total_diagnoses": 4,
        "consult_requested": True,
        "primary_diagnosis_code": "R079",
        "num_medications": 2,
        "num_medications_given": 1,
    }
    record = PatientRecordRequest(**payload)
    assert record.primary_diagnosis_code == "R079"


@pytest.mark.parametrize("missing_field", ["age", "sex", "pulse", "triage_level", "arrived_by_ambulance"])
def test_rejects_missing_required_field(missing_field):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != missing_field}
    with pytest.raises(ValidationError):
        PatientRecordRequest(**payload)


@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("age", -1),
        ("age", 200),
        ("sex", 3),
        ("pulse", -5),
        ("temperature_fahrenheit", 200.0),
        ("triage_level", 6),
        ("triage_level", 0),
    ],
)
def test_rejects_out_of_range_or_invalid_values(field, invalid_value):
    payload = {**VALID_PAYLOAD, field: invalid_value}
    with pytest.raises(ValidationError):
        PatientRecordRequest(**payload)


def test_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        PatientRecordRequest(**VALID_PAYLOAD, unexpected_field="should not be allowed")
