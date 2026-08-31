import pytest
from fastapi.testclient import TestClient
from src.domain.models import Shipment, CargoProfile
from src.db.session import SessionLocal, tenant_context
from sqlalchemy.orm import sessionmaker
from src.db.session import engine
from src.core.security import generate_signed_token
from main import app

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

def test_signed_urls_integration(rls_db_session):
    # Setup Data com a Transportadora Logix (Tenant 1)
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
    
    # CENÁRIO A: URL Perfeitamente Válida
    token_valid = generate_signed_token(shipment_id, 1)
    res = client.get(f"/api/public/handshake?token={token_valid}")
    assert res.status_code == 200, res.json()
    data = res.json()
    assert data["id"] == shipment_id
    assert "status" in data
    # Garante que NENHUMA telemetria ou dado sensível (GPS/Perfil) é vazado pelo Payload
    assert "profile" not in data
    assert "telemetry" not in data
    
    # CENÁRIO B: URL Adulterada (Motorista tenta mudar id na string, hash quebra)
    token_tampered = token_valid[:-2] + "xy"
    res = client.get(f"/api/public/handshake?token={token_tampered}")
    assert res.status_code == 403
    assert "Invalid token signature" in res.json()["detail"]
    
    # CENÁRIO C: URL Expirada
    import time
    from unittest.mock import patch
    
    # Forjamos o relógio para o token nascer há mais de 24h
    with patch('time.time', return_value=time.time() - 90000):
        expired_token = generate_signed_token(shipment_id, 1)
        
    res = client.get(f"/api/public/handshake?token={expired_token}")
    assert res.status_code == 403
    assert "Token expired" in res.json()["detail"]
