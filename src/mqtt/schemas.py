from pydantic import BaseModel
from datetime import datetime

class HandshakePayload(BaseModel):
    shipment_id: int
    receiver_id: int
    has_breached: bool
    timestamp: datetime

from typing import List, Optional

class TelemetryReading(BaseModel):
    timestamp: datetime
    temperature: int
    humidity: Optional[int] = None
    gps: Optional[str] = None

class TelemetryBatchPayload(BaseModel):
    shipment_id: int
    readings: List[TelemetryReading]
