import json
import logging

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
