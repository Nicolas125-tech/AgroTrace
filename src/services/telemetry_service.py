from sqlalchemy import insert
from sqlalchemy.orm import Session

from src.domain.models import Telemetry
from src.mqtt.schemas import TelemetryBatchPayload


def ingest_telemetry_batch(db: Session, payload: TelemetryBatchPayload):
    if not payload.readings:
        return
        
    records = []
    for reading in payload.readings:
        records.append({
            "timestamp": reading.timestamp,
            "shipment_id": payload.shipment_id,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "gps": reading.gps
        })
        
    # Usando execute com dicionários garante inserção em bulk otimizada (executemany)
    db.execute(insert(Telemetry), records)
    db.commit()
