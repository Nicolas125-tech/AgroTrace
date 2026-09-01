from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from src.db.session import engine, tenant_context
from src.domain.models import CargoProfile, CustodyTransfer, Shipment

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from main import app
from src.core.security import generate_signed_token

client = TestClient(app)

def test_seam3_ephemeral_handshake(db_session):
    # Setup Tenant 1 e Carga
    tenant_context.set(1)
    session = TestingSessionLocal()
    
    profile = CargoProfile(name="Global", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15)
    session.add(profile)
    session.commit()
    
    shipment = Shipment(tenant_id=1, profile_id=profile.id, grace_period_hours=2)
    session.add(shipment)
    session.commit()
    shipment_id = shipment.id
    session.close()
    
    # Motorista Efêmero 'Seu João' chega com o QR Code
    token = generate_signed_token(shipment_id, 1)
    
    import datetime
    retroactive_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    retroactive_iso = retroactive_time.isoformat() + "Z"
    
    payload = {
        "driver_cpf": "123.456.789-00",
        "driver_name": "João da Silva",
        "vehicle_plate": "ABC-1234",
        "offline_timestamp": retroactive_iso
    }
    
    # POST anonimizado para aceitar a custódia
    res = client.post(f"/api/public/handshake?token={token}", json=payload)
    assert res.status_code == 200, res.json()
    data = res.json()
    assert data["status"] == "success"
    assert data["custody_status"] == "pending_sync"
    
    # Verifica Auditoria: Garantir que Seu João e a data retroativa ficaram cravados
    tenant_context.set(1)
    session_verify = TestingSessionLocal()
    transfer = session_verify.query(CustodyTransfer).filter(CustodyTransfer.id == data["transfer_id"]).first()
    
    assert transfer is not None
    assert transfer.driver_cpf == "123.456.789-00"
    assert transfer.driver_name == "João da Silva"
    assert transfer.vehicle_plate == "ABC-1234"
    # Auditoria crucial: O banco cravou a hora do celular (offline), não a hora do request!
    # Removing microseconds for easy comparison
    assert transfer.initiated_at.replace(microsecond=0) == retroactive_time.replace(microsecond=0)
    
    # E claro, o Shipment foi modificado e está vinculado corretamente à Logix (Tenant 1)
    # RLS testará se o tenant 1 consegue ver.
    shipment_verify = session_verify.query(Shipment).filter(Shipment.id == shipment_id).first()
    assert shipment_verify.tenant_id == 1
    session_verify.close()
