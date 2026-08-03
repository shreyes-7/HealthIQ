import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from Backend.app.db.base import Base
from Backend.app.services import history_service

SAMPLE_PREDICTION = {
    "model_name": "lightgbm",
    "model_version": "1.0.0",
    "predicted_admission": True,
    "admission_probability": 0.82,
    "confidence_score": 0.64,
    "risk_category": "high",
    "processing_time_ms": 1234.5,
    "features_that_increased_risk": [
        {"feature": "CONSULT__Yes", "source_variable": "CONSULT", "feature_value": 1.0, "shap_value": 2.1}
    ],
    "features_that_decreased_risk": [
        {"feature": "AGE", "source_variable": "AGE", "feature_value": -0.3, "shap_value": -0.9}
    ],
}


@pytest.fixture
def db_session() -> Session:
    """An isolated in-memory database per test, independent of the
    application's configured Settings.database_url."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


def test_record_prediction_persists_expected_fields(db_session):
    record = history_service.record_prediction(db_session, SAMPLE_PREDICTION)

    assert record.id
    assert record.model_name == "lightgbm"
    assert record.risk_category == "high"
    assert record.predicted_admission is True


def test_record_prediction_does_not_store_raw_patient_input(db_session):
    record = history_service.record_prediction(db_session, SAMPLE_PREDICTION)

    stored_columns = record.__table__.columns.keys()
    assert "age" not in stored_columns
    assert "pulse" not in stored_columns


def test_list_predictions_returns_most_recent_first(db_session):
    first = history_service.record_prediction(db_session, SAMPLE_PREDICTION)
    second = history_service.record_prediction(db_session, {**SAMPLE_PREDICTION, "risk_category": "low"})

    results = history_service.list_predictions(db_session)

    assert [record.id for record in results][:2] == [second.id, first.id]


def test_list_predictions_respects_limit(db_session):
    for _ in range(5):
        history_service.record_prediction(db_session, SAMPLE_PREDICTION)

    results = history_service.list_predictions(db_session, limit=2)

    assert len(results) == 2
