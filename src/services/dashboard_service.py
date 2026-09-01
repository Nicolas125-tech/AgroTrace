from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.domain.models import Shipment, CargoProfile, CustodyTransfer, Telemetry

def get_shipment_details(db: Session, shipment_id: int):
    stmt = (
        db.query(Shipment, CargoProfile, CustodyTransfer)
        .join(CargoProfile, CargoProfile.id == Shipment.profile_id)
        .outerjoin(CustodyTransfer, CustodyTransfer.shipment_id == Shipment.id)
        .filter(Shipment.id == shipment_id)
        .order_by(CustodyTransfer.id.desc())
        .first()
    )

    if not stmt:
        return None
        
    shipment, profile, active_custody = stmt
    
    return {
        "id": shipment.id,
        "status": shipment.status.value,
        "grace_period_hours": shipment.grace_period_hours,
        "profile": {
            "name": profile.name,
            "max_temp": profile.max_temp,
            "min_temp": profile.min_temp,
            "continuous_exposure_limit_minutes": profile.continuous_exposure_limit_minutes
        },
        "custody": {
            "status": active_custody.status.value if active_custody else None,
            "initiated_at": active_custody.initiated_at.isoformat() if active_custody else None
        } if active_custody else None
    }

def get_telemetry_downsampled(db: Session, shipment_id: int, bucket_interval: str = "5 minutes"):
    """Uses TimescaleDB time_bucket to downsample raw telemetry for charting performance."""
    bucket = func.time_bucket(bucket_interval, Telemetry.timestamp).label('bucket')
    stmt = (
        select(
            bucket,
            func.avg(Telemetry.temperature).label('avg_temp'),
            func.avg(Telemetry.humidity).label('avg_hum')
        )
        .where(Telemetry.shipment_id == shipment_id)
        .group_by(bucket)
        .order_by(bucket.asc())
    )
    result = db.execute(stmt).all()
    
    return [
        {
            "timestamp": r.bucket.isoformat() if r.bucket else None,
            "temperature": round(float(r.avg_temp), 2) if r.avg_temp is not None else None,
            "humidity": round(float(r.avg_hum), 2) if r.avg_hum is not None else None
        }
        for r in result
    ]

def get_simplified_route(db: Session, shipment_id: int, bucket_interval: str = "15 minutes"):
    """Downsamples GPS coordinates to reduce map rendering overhead."""
    # Since GPS is string, we pick the first/max coordinate occurring in the bucket interval
    bucket = func.time_bucket(bucket_interval, Telemetry.timestamp).label('bucket')
    stmt = (
        select(
            bucket,
            func.max(Telemetry.gps).label('gps')
        )
        .where(Telemetry.shipment_id == shipment_id)
        .where(Telemetry.gps.isnot(None))
        .group_by(bucket)
        .order_by(bucket.asc())
    )
    result = db.execute(stmt).all()
    
    route = []
    for r in result:
        if r.gps:
            parts = r.gps.split(',')
            if len(parts) == 2:
                try:
                    route.append({
                        "lat": float(parts[0].strip()), 
                        "lng": float(parts[1].strip()), 
                        "timestamp": r.bucket.isoformat() if r.bucket else None
                    })
                except ValueError:
                    pass
    return route
