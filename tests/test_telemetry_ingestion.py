import pytest
import time
import json
from datetime import datetime
import paho.mqtt.publish as publish
from src.domain.models import Shipment, CargoProfile, Telemetry
from src.mqtt.client import MQTT_BROKER, MQTT_PORT, TELEMETRY_TOPIC
from src.db.session import SessionLocal

def test_telemetry_mqtt_integration(db_session, mqtt_client_fixture):
    # Setup test data
    profile = CargoProfile(name="TelemetryTest", max_temp=0, min_temp=-10, continuous_exposure_limit_minutes=30)
    db_session.add(profile)
    db_session.commit()
    
    shipment = Shipment(profile_id=profile.id, grace_period_hours=2)
    db_session.add(shipment)
    db_session.commit()
    
    # Payload
    payload = {
        "shipment_id": shipment.id,
        "readings": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "temperature": -15,
                "humidity": 50,
                "gps": "-23.55,-46.63"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "temperature": -14,
                "humidity": 52,
                "gps": "-23.56,-46.64"
            }
        ]
    }
    
    publish.single(TELEMETRY_TOPIC, payload=json.dumps(payload), hostname=MQTT_BROKER, port=MQTT_PORT)
    
    time.sleep(1)
    
    # Assert bulk insertion via hypertable
    db = SessionLocal()
    count = db.query(Telemetry).filter(Telemetry.shipment_id == shipment.id).count()
    assert count == 2
    db.close()
