import pytest

from datetime import datetime

from src.domain.models import (
    CargoProfile,
    CustodyStatus,
    Shipment,
    ShipmentStatus,
    CustodyTransfer,
    Telemetry,
)
from src.services.custody_service import initiate_transfer, process_fast_path_handshake, resolve_quarantined_transfer

# Conecta ao PostgreSQL/TimescaleDB no Docker


def test_initiate_transfer(db_session):
    profile = CargoProfile(name="Protein", max_temp=-18, min_temp=-30, continuous_exposure_limit_minutes=15)
    db_session.add(profile)
    db_session.commit()
    
    shipment = Shipment(tenant_id=1, profile_id=1, grace_period_hours=2)
    db_session.add(shipment)
    db_session.commit()
    
    transfer = initiate_transfer(db_session, shipment.id)
    assert transfer.status == CustodyStatus.PENDING_SYNC

def test_fast_path_handshake_rejects_and_breaches(db_session):
    # setup
    profile = CargoProfile(name="Coffee", max_temp=25, min_temp=10, continuous_exposure_limit_minutes=60)
    db_session.add(profile)
    shipment = Shipment(tenant_id=1, profile_id=1, grace_period_hours=24)
    db_session.add(shipment)
    db_session.commit()
    
    initiate_transfer(db_session, shipment.id)
    
    # Process breach via fast-path
    transfer = process_fast_path_handshake(db_session, shipment.id, has_breached=True)
    assert transfer.status == CustodyStatus.REJECTED
    
    db_session.refresh(shipment)
    assert shipment.status == ShipmentStatus.BREACHED

def test_telemetry_insert_hypertable(db_session):
    profile = CargoProfile(name="Test", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=1)
    db_session.add(profile)
    shipment = Shipment(tenant_id=1, profile_id=1, grace_period_hours=1)
    db_session.add(shipment)
    db_session.commit()
    
    # Insere leitura no Slow-Path (hypertable)
    tel = Telemetry(timestamp=datetime.utcnow(), shipment_id=shipment.id, temperature=5)
    db_session.add(tel)
    db_session.commit()
    
    assert db_session.query(Telemetry).count() > 0

def test_resolve_quarantined_transfer_accepted(db_session):
    profile = CargoProfile(name="Test", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=1)
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(tenant_id=1, profile_id=profile.id, grace_period_hours=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = CustodyTransfer(shipment_id=shipment.id, status=CustodyStatus.QUARANTINED, initiated_at=datetime.utcnow())
    db_session.add(transfer)
    db_session.commit()

    resolved_transfer = resolve_quarantined_transfer(db_session, transfer.id, CustodyStatus.ACCEPTED)

    assert resolved_transfer.status == CustodyStatus.ACCEPTED

    db_session.refresh(shipment)
    assert shipment.status == ShipmentStatus.IN_TRANSIT

def test_resolve_quarantined_transfer_rejected(db_session):
    profile = CargoProfile(name="Test", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=1)
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(tenant_id=1, profile_id=profile.id, grace_period_hours=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = CustodyTransfer(shipment_id=shipment.id, status=CustodyStatus.QUARANTINED, initiated_at=datetime.utcnow())
    db_session.add(transfer)
    db_session.commit()

    resolved_transfer = resolve_quarantined_transfer(db_session, transfer.id, CustodyStatus.REJECTED)

    assert resolved_transfer.status == CustodyStatus.REJECTED

    db_session.refresh(shipment)
    assert shipment.status == ShipmentStatus.BREACHED

def test_resolve_quarantined_transfer_invalid_status(db_session):
    profile = CargoProfile(name="Test", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=1)
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(tenant_id=1, profile_id=profile.id, grace_period_hours=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = CustodyTransfer(shipment_id=shipment.id, status=CustodyStatus.QUARANTINED, initiated_at=datetime.utcnow())
    db_session.add(transfer)
    db_session.commit()

    with pytest.raises(ValueError, match="Must resolve to ACCEPTED or REJECTED"):
        resolve_quarantined_transfer(db_session, transfer.id, CustodyStatus.PENDING_SYNC)

def test_resolve_quarantined_transfer_not_found(db_session):
    with pytest.raises(ValueError, match="Transfer not found"):
        resolve_quarantined_transfer(db_session, 9999, CustodyStatus.ACCEPTED)

def test_resolve_quarantined_transfer_not_quarantined(db_session):
    profile = CargoProfile(name="Test", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=1)
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(tenant_id=1, profile_id=profile.id, grace_period_hours=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = CustodyTransfer(shipment_id=shipment.id, status=CustodyStatus.PENDING_SYNC, initiated_at=datetime.utcnow())
    db_session.add(transfer)
    db_session.commit()

    with pytest.raises(ValueError, match="Only QUARANTINED transfers can be manually resolved."):
        resolve_quarantined_transfer(db_session, transfer.id, CustodyStatus.ACCEPTED)
