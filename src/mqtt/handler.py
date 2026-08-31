import json
import logging
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.mqtt.schemas import HandshakePayload
from src.services.custody_service import process_fast_path_handshake

logger = logging.getLogger(__name__)

def process_handshake_message(payload_bytes: bytes):
    try:
        data = json.loads(payload_bytes.decode("utf-8"))
        payload = HandshakePayload(**data)
        
        db: Session = SessionLocal()
        try:
            # Integração com FSM - a payload.has_breached ditará a mudança
            process_fast_path_handshake(db, shipment_id=payload.shipment_id, has_breached=payload.has_breached)
            logger.info(f"Successfully processed handshake for shipment {payload.shipment_id}")
        except Exception as e:
            logger.error(f"Error processing handshake logic: {e}")
            db.rollback()
        finally:
            db.close()
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Invalid MQTT payload: {e}")

from src.mqtt.schemas import TelemetryBatchPayload
from src.services.telemetry_service import ingest_telemetry_batch

def process_telemetry_message(payload_bytes: bytes):
    try:
        data = json.loads(payload_bytes.decode("utf-8"))
        payload = TelemetryBatchPayload(**data)
        
        db: Session = SessionLocal()
        try:
            ingest_telemetry_batch(db, payload)
            logger.info(f"Ingested {len(payload.readings)} telemetry readings for shipment {payload.shipment_id}")
        except Exception as e:
            logger.error(f"Error ingesting telemetry: {e}")
            db.rollback()
        finally:
            db.close()
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Invalid telemetry payload: {e}")
