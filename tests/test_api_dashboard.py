import pytest
from src.core.config import settings
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from main import app
from src.domain.models import CargoProfile, Shipment, Telemetry

client = TestClient(app)


@pytest.fixture
def dashboard_setup(db_session):
    # Setup Data
    profile = CargoProfile(
        name="DashTest", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    # Generate 60 readings (1 per minuto por 1 hora)
    base_time = datetime.now(timezone.utc) - timedelta(hours=1)
    for i in range(60):
        t = Telemetry(
            timestamp=base_time + timedelta(minutes=i),
            shipment_id=shipment.id,
            temperature=2 + (i % 3),
            humidity=50,
            gps=f"-23.550{i},-46.630{i}",
        )
        db_session.add(t)
    db_session.commit()

    from src.core.security import generate_tenant_token

    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    return {"shipment_id": shipment.id, "headers": headers}


def test_list_shipments(dashboard_setup):
    headers = dashboard_setup["headers"]
    res = client.get("/api/shipments", headers=headers)
    assert res.status_code == 200
    list_data = res.json()
    assert len(list_data) >= 1
    assert list_data[0]["status"] == "in_transit"


def test_list_shipments_with_status_filter(dashboard_setup):
    headers = dashboard_setup["headers"]
    res = client.get("/api/shipments?status=delivered", headers=headers)
    assert res.status_code == 200
    empty_list = res.json()
    assert len(empty_list) == 0


def test_get_shipment(dashboard_setup):
    shipment_id = dashboard_setup["shipment_id"]
    headers = dashboard_setup["headers"]
    res = client.get(f"/api/shipments/{shipment_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["profile"]["name"] == "DashTest"


@pytest.mark.skipif(
    "sqlite" in settings.DATABASE_URL,
    reason="Requires TimescaleDB time_bucket function",
)
def test_get_shipment_telemetry(dashboard_setup):
    shipment_id = dashboard_setup["shipment_id"]
    headers = dashboard_setup["headers"]
    res = client.get(f"/api/shipments/{shipment_id}/telemetry", headers=headers)
    assert res.status_code == 200
    telemetry_data = res.json()
    assert len(telemetry_data) == 12  # O downsampling mágico do TimescaleDB
    assert "temperature" in telemetry_data[0]


@pytest.mark.skipif(
    "sqlite" in settings.DATABASE_URL,
    reason="Requires TimescaleDB time_bucket function",
)
def test_get_shipment_route(dashboard_setup):
    shipment_id = dashboard_setup["shipment_id"]
    headers = dashboard_setup["headers"]
    res = client.get(f"/api/shipments/{shipment_id}/route", headers=headers)
    assert res.status_code == 200
    route_data = res.json()
    assert len(route_data) == 4
    assert "lat" in route_data[0]
    assert "lng" in route_data[0]


@pytest.mark.skipif(
    "sqlite" in settings.DATABASE_URL,
    reason="Requires TimescaleDB time_bucket function",
)
def test_dashboard_endpoints_idor(db_session):
    # Setup Data - Create a shipment for tenant 2, but we will login as tenant 1
    profile = CargoProfile(
        name="DashTestIDOR",
        max_temp=5,
        min_temp=0,
        continuous_exposure_limit_minutes=15,
    )
    db_session.add(profile)
    db_session.commit()

    shipment_t2 = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=2)
    db_session.add(shipment_t2)
    db_session.commit()

    t = Telemetry(
        timestamp=datetime.now(timezone.utc),
        shipment_id=shipment_t2.id,
        temperature=4,
        humidity=50,
        gps="-23.5501,-46.6301",
    )
    db_session.add(t)
    db_session.commit()

    # Login as Tenant 1
    from src.core.security import generate_tenant_token

    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    # Test GET /api/shipments/{id}/telemetry for tenant 2's shipment
    res = client.get(f"/api/shipments/{shipment_t2.id}/telemetry", headers=headers)
    assert res.status_code == 200
    telemetry_data = res.json()
    assert len(telemetry_data) == 0  # IDOR blocked!

    # Test GET /api/shipments/{id}/route for tenant 2's shipment
    res = client.get(f"/api/shipments/{shipment_t2.id}/route", headers=headers)
    assert res.status_code == 200
    route_data = res.json()
    assert len(route_data) == 0  # IDOR blocked!


def test_get_shipment_not_found(db_session):
    # Login as Tenant 1
    from src.core.security import generate_tenant_token

    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    # Test GET /api/shipments/{id} with non-existent ID
    res = client.get("/api/shipments/99999", headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Shipment not found"


def test_generate_qr_url(db_session):
    # Setup Data
    profile = CargoProfile(
        name="QRTest", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    # Login as Tenant 1
    from src.core.security import generate_tenant_token, verify_signed_token

    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    # Generate QR URL
    res = client.post(f"/api/shipments/{shipment.id}/generate-qr", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "url" in data
    assert "token" in data
    assert data["url"] == f"https://agrotrace.com/handshake?token={data['token']}"

    # Verify the token
    payload = verify_signed_token(data["token"])
    assert payload["shipment_id"] == shipment.id
    assert payload["tenant_id"] == 1


@pytest.mark.skipif(
    "sqlite" in settings.DATABASE_URL, reason="RLS is not supported in SQLite"
)
def test_generate_qr_url_not_found_or_idor(db_session):
    # Setup Data - Create a shipment for tenant 2
    profile = CargoProfile(
        name="QRTestIDOR", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.commit()

    shipment_t2 = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=2)
    db_session.add(shipment_t2)
    db_session.commit()

    # Login as Tenant 1
    from src.core.security import generate_tenant_token

    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to generate QR for tenant 2's shipment (IDOR check)
    # The current code uses a filter by shipment ID with RLS implicitly applied via the DB session.
    # Therefore, we should expect a 404 since tenant 1 cannot see tenant 2's shipment.
    res = client.post(f"/api/shipments/{shipment_t2.id}/generate-qr", headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Shipment not found"

    # Attempt to generate QR for a non-existent shipment
    res = client.post("/api/shipments/99999/generate-qr", headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Shipment not found"
