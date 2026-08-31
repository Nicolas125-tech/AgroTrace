import pytest
import time
import json
from datetime import datetime
import paho.mqtt.publish as publish
from src.domain.models import Shipment, CargoProfile, CustodyTransfer, CustodyStatus, ShipmentStatus
from src.services.custody_service import initiate_transfer
from src.mqtt.client import start_mqtt_client, MQTT_BROKER, MQTT_PORT, HANDSHAKE_TOPIC
from src.db.session import SessionLocal

@pytest.fixture(scope="module")
def mqtt_client_fixture():
    # Inicia o loop em background conectando ao Mosquitto no Docker
    client = start_mqtt_client()
    yield client
    client.loop_stop()
    client.disconnect()

def test_mqtt_handshake_integration(db_session, mqtt_client_fixture):
    # Setup test data no PostgreSQL real
    profile = CargoProfile(name="IntegrationTest", max_temp=0, min_temp=-10, continuous_exposure_limit_minutes=30)
    db_session.add(profile)
    db_session.commit()
    
    shipment = Shipment(profile_id=profile.id, grace_period_hours=2)
    db_session.add(shipment)
    db_session.commit()
    
    # Coloca em PENDING_SYNC
    initiate_transfer(db_session, shipment.id)
    
    # Cria o Payload de Ruptura (has_breached = True) validável pelo Pydantic
    payload = {
        "shipment_id": shipment.id,
        "receiver_id": 999,
        "has_breached": True,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Publica no broker (simulando a borda)
    publish.single(HANDSHAKE_TOPIC, payload=json.dumps(payload), hostname=MQTT_BROKER, port=MQTT_PORT)
    
    # Aguarda o worker ler, validar com Pydantic, atualizar no Postgres via SQLAlchemy FSM
    time.sleep(1)
    
    # Assert state change
    db_session.refresh(shipment)
    updated_transfer = db_session.query(CustodyTransfer).filter(
        CustodyTransfer.shipment_id == shipment.id, 
        CustodyTransfer.status != CustodyStatus.PENDING_SYNC
    ).first()
    
    assert shipment.status == ShipmentStatus.BREACHED
    assert updated_transfer is not None
    assert updated_transfer.status == CustodyStatus.REJECTED
