import pytest
from datetime import datetime, timezone

from src.domain.models import CargoProfile, CustodyTransfer, Shipment
from src.services.dashboard_service import get_shipment_details

def test_get_shipment_details_found(db_session):
    # Setup Data
    profile = CargoProfile(
        name="ServiceTestProfile",
        max_temp=10,
        min_temp=2,
        continuous_exposure_limit_minutes=30
    )
    db_session.add(profile)
    db_session.flush()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=4, tenant_id=1)
    db_session.add(shipment)
    db_session.flush()

    custody = CustodyTransfer(
        shipment_id=shipment.id,
        status="accepted",
        initiated_at=datetime.now(timezone.utc)
    )
    db_session.add(custody)
    db_session.commit()

    # Test
    details = get_shipment_details(db_session, shipment.id)

    assert details is not None
    assert details["id"] == shipment.id
    assert details["status"] == "in_transit"  # Default status for new shipment
    assert details["grace_period_hours"] == 4

    assert details["profile"]["name"] == "ServiceTestProfile"
    assert details["profile"]["max_temp"] == 10
    assert details["profile"]["min_temp"] == 2
    assert details["profile"]["continuous_exposure_limit_minutes"] == 30

    assert details["custody"] is not None
    assert details["custody"]["status"] == "accepted"
    assert "initiated_at" in details["custody"]


def test_get_shipment_details_no_custody(db_session):
    # Setup Data
    profile = CargoProfile(
        name="NoCustodyProfile",
        max_temp=5,
        min_temp=0,
        continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.flush()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    # Test
    details = get_shipment_details(db_session, shipment.id)

    assert details is not None
    assert details["id"] == shipment.id
    assert details["profile"]["name"] == "NoCustodyProfile"
    assert details["custody"] is None


def test_get_shipment_details_not_found(db_session):
    # Test
    details = get_shipment_details(db_session, 99999)
    assert details is None
