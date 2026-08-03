import logging

from fastapi.testclient import TestClient

from Backend.app.core.config import Settings
from Backend.app.core.logging import configure_logging, get_logger
from Backend.app.main import app

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


def test_configure_logging_sets_level_and_is_idempotent():
    configure_logging(Settings(log_level="DEBUG"))
    logger = get_logger()
    handler_count = len(logger.handlers)

    configure_logging(Settings(log_level="DEBUG"))

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == handler_count


def test_prediction_log_entry_never_contains_patient_field_values(caplog):
    with caplog.at_level(logging.INFO, logger="healthiq.backend"):
        with TestClient(app) as client:
            client.post("/api/v1/predict", json=VALID_PAYLOAD)

    prediction_logs = [record.message for record in caplog.records if "Prediction served" in record.message]
    assert len(prediction_logs) == 1

    log_message = prediction_logs[0]
    assert "98.6" not in log_message  # submitted temperature
    assert "130" not in log_message  # submitted systolic_bp
    assert "risk_category=" in log_message
    assert "model_version=" in log_message
