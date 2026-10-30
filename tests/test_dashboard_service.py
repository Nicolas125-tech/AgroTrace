import pytest
from datetime import datetime, timedelta, timezone
from src.core.config import settings
from src.domain.models import CargoProfile, Shipment, Telemetry
from src.services.dashboard_service import get_telemetry_downsampled


@pytest.mark.skipif(
    "sqlite" in settings.DATABASE_URL,
    reason="Requires TimescaleDB time_bucket function",
)
def test_get_telemetry_downsampled(db_session):
    # Setup Data
    profile = CargoProfile(
        name="TestProfile", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.flush()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.flush()

    # Create telemetry spanning across 2 buckets (10 minutes total, 5 minutes each)
    base_time = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)

    # Bucket 1: 12:00 -> 12:04
    # Temps: 2, 4 -> Avg: 3
    # Hum: 50, 60 -> Avg: 55
    t1 = Telemetry(
        timestamp=base_time, shipment_id=shipment.id, temperature=2, humidity=50
    )
    t2 = Telemetry(
        timestamp=base_time + timedelta(minutes=2),
        shipment_id=shipment.id,
        temperature=4,
        humidity=60,
    )

    # Bucket 2: 12:05 -> 12:09
    # Temps: 6, 8 -> Avg: 7
    # Hum: 70, 80 -> Avg: 75
    t3 = Telemetry(
        timestamp=base_time + timedelta(minutes=5),
        shipment_id=shipment.id,
        temperature=6,
        humidity=70,
    )
    t4 = Telemetry(
        timestamp=base_time + timedelta(minutes=7),
        shipment_id=shipment.id,
        temperature=8,
        humidity=80,
    )

    db_session.add_all([t1, t2, t3, t4])
    db_session.commit()

    # Action
    results = get_telemetry_downsampled(
        db_session, shipment.id, bucket_interval="5 minutes"
    )

    # Assert
    assert len(results) == 2

    assert results[0]["temperature"] == 3.0
    assert results[0]["humidity"] == 55.0
    assert results[0]["timestamp"] == "2023-01-01T12:00:00+00:00"

    assert results[1]["temperature"] == 7.0
    assert results[1]["humidity"] == 75.0
    assert results[1]["timestamp"] == "2023-01-01T12:05:00+00:00"


@pytest.mark.skipif(
    "sqlite" in settings.DATABASE_URL,
    reason="Requires TimescaleDB time_bucket function",
)
def test_get_telemetry_downsampled_empty(db_session):
    # Setup Data
    profile = CargoProfile(
        name="EmptyProfile",
        max_temp=5,
        min_temp=0,
        continuous_exposure_limit_minutes=15,
    )
    db_session.add(profile)
    db_session.flush()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    # Action
    results = get_telemetry_downsampled(
        db_session, shipment.id, bucket_interval="5 minutes"
    )

    # Assert
    assert results == []
