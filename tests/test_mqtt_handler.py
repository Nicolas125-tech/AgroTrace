import json
import logging
from unittest.mock import patch

from src.mqtt.handler import process_handshake_message, process_telemetry_message



from datetime import datetime, timezone

def test_process_handshake_happy_path(caplog):
    caplog.set_level(logging.INFO)

    valid_payload = json.dumps({
        "shipment_id": 123,
        "receiver_id": 456,
        "has_breached": False,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }).encode("utf-8")

    with patch("src.mqtt.handler.process_fast_path_handshake") as mock_process:
        process_handshake_message(valid_payload)

        # Verify the mock was called correctly
        mock_process.assert_called_once()
        _args, kwargs = mock_process.call_args
        assert kwargs.get("shipment_id") == 123
        assert kwargs.get("has_breached") is False

        # Verify the log message
        assert "Successfully processed handshake for shipment 123" in caplog.text


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


def test_process_handshake_error_path(caplog):
    caplog.set_level(logging.ERROR)

    payload = json.dumps(
        {
            "shipment_id": 123,
            "receiver_id": 456,
            "has_breached": False,
            "timestamp": "2023-10-27T10:00:00Z",
        }
    ).encode("utf-8")

    with patch("src.mqtt.handler.process_fast_path_handshake") as mock_process:
        mock_process.side_effect = Exception("Test Error")

        with patch("src.mqtt.handler.SessionLocal") as mock_session_local:
            mock_session = mock_session_local.return_value

            process_handshake_message(payload)

            mock_session.rollback.assert_called_once()

    assert "Error processing handshake logic: Test Error" in caplog.text


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
