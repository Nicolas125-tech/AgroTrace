from fastapi.testclient import TestClient

from main import app
from src.core.security import get_password_hash
from src.domain.models import Tenant, TenantRole

client = TestClient(app)

def test_login_tenant(db_session):
    tenant = Tenant(
        name="Agro Corp",
        username="agro_corp",
        hashed_password=get_password_hash("secure_password"),
        role=TenantRole.PRODUCER
    )
    db_session.add(tenant)
    db_session.commit()

    response = client.post("/api/auth/login", json={
        "username": "agro_corp",
        "password": "secure_password"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(db_session):
    tenant = Tenant(
        name="Agro Corp",
        username="agro_corp2",
        hashed_password=get_password_hash("secure_password"),
        role=TenantRole.PRODUCER
    )
    db_session.add(tenant)
    db_session.commit()

    response = client.post("/api/auth/login", json={
        "username": "agro_corp2",
        "password": "wrong"
    })
    
    assert response.status_code == 401
