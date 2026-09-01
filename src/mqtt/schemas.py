from datetime import datetime

from pydantic import BaseModel


class HandshakePayload(BaseModel):
    shipment_id: int
    receiver_id: int
    has_breached: bool
    timestamp: datetime



class TelemetryReading(BaseModel):
    timestamp: datetime
    temperature: int
    humidity: int | None = None
    gps: str | None = None

class TelemetryBatchPayload(BaseModel):
    shipment_id: int
    readings: list[TelemetryReading]
