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
        role=TenantRole.PRODUCER,
    )
    db_session.add(tenant)
    db_session.commit()

    response = client.post(
        "/api/auth/login", json={"username": "agro_corp", "password": "secure_password"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(db_session):
    tenant = Tenant(
        name="Agro Corp",
        username="agro_corp2",
        hashed_password=get_password_hash("secure_password"),
        role=TenantRole.PRODUCER,
    )
    db_session.add(tenant)
    db_session.commit()

    response = client.post(
        "/api/auth/login", json={"username": "agro_corp2", "password": "wrong"}
    )

    assert response.status_code == 401


def test_login_rate_limiting(db_session):
    tenant = Tenant(
        name="Agro Corp 3",
        username="agro_corp3",
        hashed_password=get_password_hash("secure_password"),
        role=TenantRole.PRODUCER,
    )
    db_session.add(tenant)
    db_session.commit()

    from src.core.rate_limiting import limiter

    # Reset limiter for this specific key
    limiter.reset()

    # The slowapi get_remote_address will resolve to testclient or 127.0.0.1
    # 5/minute limit means 5 requests should pass/fail normally (we use wrong password to not rely on auth logic)
    for _ in range(5):
        response = client.post(
            "/api/auth/login", json={"username": "agro_corp3", "password": "wrong"}
        )
        assert response.status_code == 401

    # 6th attempt should be rate limited
    response = client.post(
        "/api/auth/login", json={"username": "agro_corp3", "password": "wrong"}
    )
    assert response.status_code == 429
