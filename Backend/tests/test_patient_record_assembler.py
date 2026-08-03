import pandas as pd
import pytest

from Backend.app.schemas.patient import PatientRecordRequest
from Backend.app.services.explanation_service import ExplanationRuntime
from Backend.app.services.patient_record_assembler import PatientRecordAssembler
from ML.explainability.artifacts import load_feature_names, load_preprocessing_pipeline

MINIMAL_REQUEST = PatientRecordRequest(
    age=67,
    sex=2,
    pulse=88,
    temperature_fahrenheit=98.6,
    respiratory_rate=18,
    systolic_bp=130,
    diastolic_bp=80,
    triage_level=2,
    arrived_by_ambulance=True,
)


@pytest.fixture(scope="module")
def assembler() -> PatientRecordAssembler:
    return PatientRecordAssembler()


def test_assembled_record_has_every_raw_column(assembler):
    record = assembler.assemble(MINIMAL_REQUEST)

    assert record.shape[0] == 1
    assert record.shape[1] == 913


def test_unset_fields_are_null(assembler):
    record = assembler.assemble(MINIMAL_REQUEST)

    assert pd.isna(record["NUMDIS"].iloc[0])
    assert pd.isna(record["DIAG1"].iloc[0])


def test_temperature_is_converted_to_implied_decimal(assembler):
    record = assembler.assemble(MINIMAL_REQUEST)

    assert record["TEMPF"].iloc[0] == pytest.approx(986.0)


def test_ambulance_boolean_maps_to_nhamcs_code(assembler):
    arrived = assembler.assemble(MINIMAL_REQUEST)
    not_arrived = assembler.assemble(MINIMAL_REQUEST.model_copy(update={"arrived_by_ambulance": False}))

    assert arrived["ARREMS"].iloc[0] == 1
    assert not_arrived["ARREMS"].iloc[0] == 2


def test_assembled_record_transforms_with_zero_missing_expected_features(assembler):
    """The empirical proof this design relies on: a mostly-null raw record
    (only the curated fields set) must still produce every expected model
    feature with no NaNs, via the pipeline's own imputation."""
    pipeline = load_preprocessing_pipeline()
    feature_names = load_feature_names()

    record = assembler.assemble(MINIMAL_REQUEST)
    result = pipeline.transform(record)
    features = result["features"][feature_names]

    assert features.shape == (1, 866)
    assert features.isna().sum().sum() == 0


def test_assembled_record_produces_a_prediction_end_to_end(assembler):
    runtime = ExplanationRuntime()
    record = assembler.assemble(MINIMAL_REQUEST)

    explanation = runtime.explain_raw_patient(record)

    assert 0.0 <= explanation["predicted_probability"] <= 1.0
