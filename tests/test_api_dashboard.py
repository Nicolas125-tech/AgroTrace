import pytest
from fastapi.testclient import TestClient
from main import app
from src.domain.models import Shipment, CargoProfile, Telemetry
from src.db.session import SessionLocal
from datetime import datetime, timedelta

client = TestClient(app)

def test_dashboard_endpoints(db_session):
    # Setup Data
    profile = CargoProfile(name="DashTest", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15)
    db_session.add(profile)
    db_session.commit()
    
    shipment = Shipment(profile_id=profile.id, grace_period_hours=2)
    db_session.add(shipment)
    db_session.commit()
    
    # Generate 60 readings (1 per minuto por 1 hora)
    base_time = datetime.utcnow() - timedelta(hours=1)
    for i in range(60):
        t = Telemetry(
            timestamp=base_time + timedelta(minutes=i),
            shipment_id=shipment.id,
            temperature=2 + (i % 3),
            humidity=50,
            gps=f"-23.550{i},-46.630{i}"
        )
        db_session.add(t)
    db_session.commit()
    
    # Test GET /api/shipments/{id}
    res = client.get(f"/api/shipments/{shipment.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["profile"]["name"] == "DashTest"
    
    # Test GET /api/shipments/{id}/telemetry (default 5 minutos -> 60/5 = 12 buckets)
    res = client.get(f"/api/shipments/{shipment.id}/telemetry")
    assert res.status_code == 200
    telemetry_data = res.json()
    assert len(telemetry_data) == 12 # O downsampling mágico do TimescaleDB
    assert "temperature" in telemetry_data[0]
    
    # Test GET /api/shipments/{id}/route (default 15 minutos -> 60/15 = 4 buckets)
    res = client.get(f"/api/shipments/{shipment.id}/route")
    assert res.status_code == 200
    route_data = res.json()
    assert len(route_data) == 4
    assert "lat" in route_data[0]
    assert "lng" in route_data[0]
