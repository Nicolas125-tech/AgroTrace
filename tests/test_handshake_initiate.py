from fastapi.testclient import TestClient

from main import app
from src.domain.models import CargoProfile, Shipment, CustodyStatus, ShipmentStatus
from src.core.security import generate_tenant_token

client = TestClient(app)


def test_handshake_initiate_success(db_session):
    # Create cargo profile
    profile = CargoProfile(
        name="Test Cargo", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.flush()

    # Create shipment
    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        f"/api/shipments/{shipment.id}/handshake/initiate", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "transfer_id" in data
    assert data["transfer_status"] == CustodyStatus.PENDING_SYNC.value


def test_handshake_initiate_shipment_not_found(db_session):
    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/shipments/999/handshake/initiate", headers=headers)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Shipment not found"


def test_handshake_initiate_shipment_breached(db_session):
    # Create cargo profile
    profile = CargoProfile(
        name="Test Cargo", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.flush()

    # Create breached shipment
    shipment = Shipment(
        profile_id=profile.id,
        grace_period_hours=2,
        tenant_id=1,
        status=ShipmentStatus.BREACHED,
    )
    db_session.add(shipment)
    db_session.commit()

    token = generate_tenant_token(tenant_id=1, role="producer")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        f"/api/shipments/{shipment.id}/handshake/initiate", headers=headers
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Cannot transfer custody of a breached shipment."
