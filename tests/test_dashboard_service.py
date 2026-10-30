import pytest
from datetime import datetime, timezone, timedelta
from src.core.config import settings
from src.domain.models import CargoProfile, Shipment, Telemetry
from src.services.dashboard_service import get_simplified_route


@pytest.mark.skipif(
    "sqlite" in settings.DATABASE_URL,
    reason="Requires TimescaleDB time_bucket function",
)
def test_get_simplified_route(db_session):
    # Set up basic data
    profile = CargoProfile(
        name="RouteTest", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15
    )
    db_session.add(profile)
    db_session.commit()

    shipment = Shipment(profile_id=profile.id, grace_period_hours=2, tenant_id=1)
    db_session.add(shipment)
    db_session.commit()

    base_time = datetime.now(timezone.utc) - timedelta(hours=1)

    # 1. Valid GPS
    t1 = Telemetry(
        timestamp=base_time,
        shipment_id=shipment.id,
        temperature=2,
        humidity=50,
        gps="-23.5501,-46.6301",
    )
    # 2. Null GPS (Should be filtered in SQL)
    t2 = Telemetry(
        timestamp=base_time + timedelta(minutes=16),  # Next bucket
        shipment_id=shipment.id,
        temperature=2,
        humidity=50,
        gps=None,
    )
    # 3. Invalid GPS format (No comma)
    t3 = Telemetry(
        timestamp=base_time + timedelta(minutes=31),  # Next bucket
        shipment_id=shipment.id,
        temperature=2,
        humidity=50,
        gps="invalid_gps",
    )
    # 4. Invalid GPS format (Not floats)
    t4 = Telemetry(
        timestamp=base_time + timedelta(minutes=46),  # Next bucket
        shipment_id=shipment.id,
        temperature=2,
        humidity=50,
        gps="lat,lng",
    )

    db_session.add_all([t1, t2, t3, t4])
    db_session.commit()

    route = get_simplified_route(db_session, shipment.id, bucket_interval="15 minutes")

    # Only t1 has valid gps data. t2 is null. t3 and t4 are invalid.
    assert len(route) == 1
    assert route[0]["lat"] == -23.5501
    assert route[0]["lng"] == -46.6301
    assert "timestamp" in route[0]
