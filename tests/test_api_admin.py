from fastapi.testclient import TestClient

from main import app
from src.core.security import generate_tenant_token
from src.domain.models import CargoProfile, CustodyStatus, Shipment
from src.services.custody_service import initiate_transfer

client = TestClient(app)


def test_resolve_quarantined_accepted(db_session):
    # Setup
    profile = CargoProfile(
        name="Quarantine Test",
        max_temp=10,
        min_temp=0,
        continuous_exposure_limit_minutes=60,
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    transfer.status = CustodyStatus.QUARANTINED
    db_session.commit()

    token = generate_tenant_token(tenant_id=1, role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        f"/api/admin/transfers/{transfer.id}/resolve?force_status=accepted",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["new_status"] == "accepted"

    db_session.refresh(transfer)
    assert transfer.status == CustodyStatus.ACCEPTED


def test_resolve_quarantined_rejected(db_session):
    # Setup
    profile = CargoProfile(
        name="Quarantine Test Reject",
        max_temp=10,
        min_temp=0,
        continuous_exposure_limit_minutes=60,
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    transfer.status = CustodyStatus.QUARANTINED
    db_session.commit()

    token = generate_tenant_token(tenant_id=1, role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        f"/api/admin/transfers/{transfer.id}/resolve?force_status=rejected",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["new_status"] == "rejected"

    db_session.refresh(transfer)
    assert transfer.status == CustodyStatus.REJECTED


def test_resolve_quarantined_invalid_status(db_session):
    # Setup
    profile = CargoProfile(
        name="Quarantine Test Invalid",
        max_temp=10,
        min_temp=0,
        continuous_exposure_limit_minutes=60,
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    transfer.status = CustodyStatus.QUARANTINED
    db_session.commit()

    token = generate_tenant_token(tenant_id=1, role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        f"/api/admin/transfers/{transfer.id}/resolve?force_status=pending_sync",
        headers=headers,
    )
    assert res.status_code == 400
    data = res.json()
    assert "Must resolve to ACCEPTED or REJECTED" in data["detail"]


def test_resolve_quarantined_not_found(db_session):
    token = generate_tenant_token(tenant_id=1, role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/admin/transfers/999/resolve?force_status=accepted", headers=headers
    )
    assert res.status_code == 400
    data = res.json()
    assert "Transfer not found" in data["detail"]
