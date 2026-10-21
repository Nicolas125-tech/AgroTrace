import pytest
from datetime import datetime

from src.domain.models import (
    CargoProfile,
    CustodyStatus,
    Shipment,
    ShipmentStatus,
    Telemetry,
)
from src.services.custody_service import initiate_transfer, process_fast_path_handshake

# Conecta ao PostgreSQL/TimescaleDB no Docker


def test_initiate_transfer(db_session):
    profile = CargoProfile(
        name="Protein", max_temp=-18, min_temp=-30, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    assert transfer.status == CustodyStatus.PENDING_SYNC


def test_fast_path_handshake_rejects_and_breaches(db_session):
    # setup
    profile = CargoProfile(
        name="Coffee", max_temp=25, min_temp=10, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    initiate_transfer(db_session, shipment.id)

    # Process breach via fast-path
    transfer = process_fast_path_handshake(db_session, shipment.id, has_breached=True)
    assert transfer.status == CustodyStatus.REJECTED

    db_session.refresh(shipment)
    assert shipment.status == ShipmentStatus.BREACHED


def test_telemetry_insert_hypertable(db_session):
    profile = CargoProfile(
        name="Test", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=1
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=1, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    # Insere leitura no Slow-Path (hypertable)
    tel = Telemetry(timestamp=datetime.utcnow(), shipment_id=shipment.id, temperature=5)
    db_session.add(tel)
    db_session.commit()

    assert db_session.query(Telemetry).count() > 0


def test_initiate_transfer_invalid_shipment(db_session):
    with pytest.raises(ValueError, match="Shipment not found"):
        initiate_transfer(db_session, shipment_id=999)


def test_resolve_quarantined_transfer_accepted(db_session):
    # Setup
    profile = CargoProfile(
        name="Apples", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    transfer.status = CustodyStatus.QUARANTINED
    db_session.commit()

    from src.services.custody_service import resolve_quarantined_transfer

    resolved_transfer = resolve_quarantined_transfer(
        db_session, transfer.id, CustodyStatus.ACCEPTED
    )

    assert resolved_transfer.status == CustodyStatus.ACCEPTED
    db_session.refresh(shipment)
    assert shipment.status == ShipmentStatus.IN_TRANSIT


def test_resolve_quarantined_transfer_rejected(db_session):
    # Setup
    profile = CargoProfile(
        name="Bananas", max_temp=15, min_temp=5, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    transfer.status = CustodyStatus.QUARANTINED
    db_session.commit()

    from src.services.custody_service import resolve_quarantined_transfer

    resolved_transfer = resolve_quarantined_transfer(
        db_session, transfer.id, CustodyStatus.REJECTED
    )

    assert resolved_transfer.status == CustodyStatus.REJECTED
    db_session.refresh(shipment)
    assert shipment.status == ShipmentStatus.BREACHED


def test_resolve_quarantined_transfer_invalid_status(db_session):
    # Setup
    profile = CargoProfile(
        name="Cherries", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    transfer.status = CustodyStatus.QUARANTINED
    db_session.commit()

    from src.services.custody_service import resolve_quarantined_transfer

    with pytest.raises(ValueError, match="Must resolve to ACCEPTED or REJECTED"):
        resolve_quarantined_transfer(
            db_session, transfer.id, CustodyStatus.PENDING_SYNC
        )


def test_resolve_quarantined_transfer_not_found(db_session):
    from src.services.custody_service import resolve_quarantined_transfer

    with pytest.raises(ValueError, match="Transfer not found"):
        resolve_quarantined_transfer(
            db_session, transfer_id=999, new_status=CustodyStatus.ACCEPTED
        )


def test_resolve_quarantined_transfer_not_quarantined(db_session):
    # Setup
    profile = CargoProfile(
        name="Dates", max_temp=25, min_temp=15, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    # transfer.status is PENDING_SYNC by default

    from src.services.custody_service import resolve_quarantined_transfer

    with pytest.raises(
        ValueError, match="Only QUARANTINED transfers can be manually resolved."
    ):
        resolve_quarantined_transfer(db_session, transfer.id, CustodyStatus.ACCEPTED)


def test_timeout_pending_transfers_stale(db_session):
    from src.services.custody_service import timeout_pending_transfers
    from datetime import timedelta

    # Setup
    profile = CargoProfile(
        name="Oranges", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    # Make it stale (>24 hours)
    transfer.initiated_at = datetime.utcnow() - timedelta(hours=25)
    db_session.commit()

    stale_transfers = timeout_pending_transfers(db_session, timeout_hours=24)

    assert len(stale_transfers) == 1
    assert stale_transfers[0].id == transfer.id
    db_session.refresh(transfer)
    assert transfer.status == CustodyStatus.QUARANTINED


def test_timeout_pending_transfers_fresh(db_session):
    from src.services.custody_service import timeout_pending_transfers
    from datetime import timedelta

    # Setup
    profile = CargoProfile(
        name="Lemons", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    # Make it fresh (<24 hours)
    transfer.initiated_at = datetime.utcnow() - timedelta(hours=23)
    db_session.commit()

    stale_transfers = timeout_pending_transfers(db_session, timeout_hours=24)

    assert len(stale_transfers) == 0
    db_session.refresh(transfer)
    assert transfer.status == CustodyStatus.PENDING_SYNC


def test_timeout_pending_transfers_ignored_statuses(db_session):
    from src.services.custody_service import timeout_pending_transfers
    from datetime import timedelta

    # Setup
    profile = CargoProfile(
        name="Limes", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    # Make it stale but ACCEPTED
    transfer.initiated_at = datetime.utcnow() - timedelta(hours=25)
    transfer.status = CustodyStatus.ACCEPTED
    db_session.commit()

    stale_transfers = timeout_pending_transfers(db_session, timeout_hours=24)

    assert len(stale_transfers) == 0
    db_session.refresh(transfer)
    assert transfer.status == CustodyStatus.ACCEPTED


def test_timeout_pending_transfers_custom_timeout(db_session):
    from src.services.custody_service import timeout_pending_transfers
    from datetime import timedelta

    # Setup
    profile = CargoProfile(
        name="Peaches", max_temp=10, min_temp=0, continuous_exposure_limit_minutes=60
    )
    db_session.add(profile)
    db_session.flush()
    shipment = Shipment(profile_id=profile.id, grace_period_hours=24, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    transfer = initiate_transfer(db_session, shipment.id)
    # Make it stale according to a custom 12-hour timeout
    transfer.initiated_at = datetime.utcnow() - timedelta(hours=13)
    db_session.commit()

    stale_transfers = timeout_pending_transfers(db_session, timeout_hours=12)

    assert len(stale_transfers) == 1
    assert stale_transfers[0].id == transfer.id
    db_session.refresh(transfer)
    assert transfer.status == CustodyStatus.QUARANTINED
