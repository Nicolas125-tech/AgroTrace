import json
import logging
from unittest.mock import patch, MagicMock

from src.mqtt.handler import process_handshake_message, process_telemetry_message


def test_process_handshake_invalid_json(caplog):
    caplog.set_level(logging.ERROR)

    # Passing invalid JSON bytes
    process_handshake_message(b"invalid json")

    assert "Invalid MQTT payload" in caplog.text


def test_process_handshake_validation_error(caplog):
    caplog.set_level(logging.ERROR)

    # Valid JSON, but missing required fields
    invalid_payload = json.dumps({"shipment_id": 123}).encode("utf-8")
    process_handshake_message(invalid_payload)

    assert "Invalid MQTT payload" in caplog.text


def test_process_telemetry_invalid_json(caplog):
    caplog.set_level(logging.ERROR)

    # Passing invalid JSON bytes
    process_telemetry_message(b"invalid json")

    assert "Invalid telemetry payload" in caplog.text


def test_process_telemetry_validation_error(caplog):
    caplog.set_level(logging.ERROR)

    # Valid JSON, but missing required fields
    invalid_payload = json.dumps({"shipment_id": 123}).encode("utf-8")
    process_telemetry_message(invalid_payload)

    assert "Invalid telemetry payload" in caplog.text


def test_process_telemetry_happy_path(caplog):
    caplog.set_level(logging.INFO)

    payload_data = {
        "shipment_id": 1,
        "readings": [{"timestamp": "2023-01-01T12:00:00Z", "temperature": 5}],
    }
    payload_bytes = json.dumps(payload_data).encode("utf-8")

    with (
        patch("src.mqtt.handler.SessionLocal") as mock_session_local,
        patch("src.mqtt.handler.ingest_telemetry_batch") as mock_ingest,
    ):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        process_telemetry_message(payload_bytes)

        # Verify SessionLocal was called
        mock_session_local.assert_called_once()

        # Verify ingest_telemetry_batch was called
        mock_ingest.assert_called_once()
        args, _ = mock_ingest.call_args
        assert args[0] == mock_db
        assert args[1].shipment_id == 1
        assert len(args[1].readings) == 1
        assert args[1].readings[0].temperature == 5

        # Verify db.close() was called
        mock_db.close.assert_called_once()
        mock_db.rollback.assert_not_called()

        assert "Ingested 1 telemetry readings for shipment 1" in caplog.text
