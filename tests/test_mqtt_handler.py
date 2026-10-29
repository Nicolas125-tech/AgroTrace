import json
import logging
from unittest.mock import patch, MagicMock

from src.mqtt.handler import process_handshake_message, process_telemetry_message


def test_process_handshake_invalid_json(caplog):
    caplog.set_level(logging.ERROR)
    process_handshake_message(b"invalid json")
    assert "Invalid MQTT payload" in caplog.text


def test_process_handshake_validation_error(caplog):
    caplog.set_level(logging.ERROR)
    invalid_payload = json.dumps({"shipment_id": 123}).encode("utf-8")
    process_handshake_message(invalid_payload)
    assert "Invalid MQTT payload" in caplog.text


def test_process_telemetry_invalid_json(caplog):
    caplog.set_level(logging.ERROR)
    process_telemetry_message(b"invalid json")
    assert "Invalid telemetry payload" in caplog.text


def test_process_telemetry_validation_error(caplog):
    caplog.set_level(logging.ERROR)
    invalid_payload = json.dumps({"shipment_id": 123}).encode("utf-8")
    process_telemetry_message(invalid_payload)
    assert "Invalid telemetry payload" in caplog.text


@patch("src.mqtt.handler.ingest_telemetry_batch")
@patch("src.mqtt.handler.SessionLocal")
def test_process_telemetry_exception(mock_session_local, mock_ingest, caplog):
    caplog.set_level(logging.ERROR)

    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_ingest.side_effect = Exception("Ingestion failed")

    valid_payload = json.dumps(
        {
            "shipment_id": 123,
            "readings": [
                {
                    "timestamp": "2023-01-01T00:00:00Z",
                    "temperature": 25,
                    "humidity": 50,
                    "gps": "12.34,56.78",
                }
            ],
        }
    ).encode("utf-8")

    process_telemetry_message(valid_payload)

    assert "Error ingesting telemetry: Ingestion failed" in caplog.text
    mock_db.rollback.assert_called_once()
    mock_db.close.assert_called_once()
