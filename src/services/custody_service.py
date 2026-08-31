from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from src.domain.models import Shipment, CustodyTransfer, ShipmentStatus, CustodyStatus

def initiate_transfer(db: Session, shipment_id: int, driver_cpf: str = None, driver_name: str = None, vehicle_plate: str = None, offline_timestamp: datetime = None) -> CustodyTransfer:
    """
    Called when a QR code is scanned. Sets the custody to Pending Sync.
    Uses offline_timestamp if provided (to support mobile offline scanning), otherwise uses current UTC time.
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise ValueError("Shipment not found")
        
    if shipment.status == ShipmentStatus.BREACHED:
        raise ValueError("Cannot transfer custody of a breached shipment.")

    transfer = CustodyTransfer(
        shipment_id=shipment_id,
        status=CustodyStatus.PENDING_SYNC,
        initiated_at=offline_timestamp if offline_timestamp else datetime.utcnow(),
        driver_cpf=driver_cpf,
        driver_name=driver_name,
        vehicle_plate=vehicle_plate
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer

def process_fast_path_handshake(db: Session, shipment_id: int, has_breached: bool) -> CustodyTransfer:
    """
    Fast-path MQTT validation. Resolves the pending custody.
    """
    # Find the active PENDING_SYNC transfer
    transfer = db.query(CustodyTransfer).filter(
        CustodyTransfer.shipment_id == shipment_id,
        CustodyTransfer.status == CustodyStatus.PENDING_SYNC
    ).order_by(CustodyTransfer.id.desc()).first()

    if not transfer:
        raise ValueError("No pending custody transfer found for this shipment.")

    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()

    if has_breached:
        transfer.status = CustodyStatus.REJECTED
        shipment.status = ShipmentStatus.BREACHED
    else:
        transfer.status = CustodyStatus.ACCEPTED

    db.commit()
    db.refresh(transfer)
    return transfer

def timeout_pending_transfers(db: Session, timeout_hours: int = 24) -> List[CustodyTransfer]:
    """
    Cron job logic: finds PENDING_SYNC > 24h and moves them to QUARANTINED.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=timeout_hours)
    
    stale_transfers = db.query(CustodyTransfer).filter(
        CustodyTransfer.status == CustodyStatus.PENDING_SYNC,
        CustodyTransfer.initiated_at < cutoff_time
    ).all()

    for transfer in stale_transfers:
        transfer.status = CustodyStatus.QUARANTINED
        
    db.commit()
    return stale_transfers

def resolve_quarantined_transfer(db: Session, transfer_id: int, new_status: CustodyStatus) -> CustodyTransfer:
    """
    Manual override for quarantined transfers.
    """
    if new_status not in [CustodyStatus.ACCEPTED, CustodyStatus.REJECTED]:
        raise ValueError("Must resolve to ACCEPTED or REJECTED")

    transfer = db.query(CustodyTransfer).filter(CustodyTransfer.id == transfer_id).first()
    if not transfer:
        raise ValueError("Transfer not found")
        
    if transfer.status != CustodyStatus.QUARANTINED:
        raise ValueError("Only QUARANTINED transfers can be manually resolved.")

    transfer.status = new_status
    if new_status == CustodyStatus.REJECTED:
        shipment = db.query(Shipment).filter(Shipment.id == transfer.shipment_id).first()
        shipment.status = ShipmentStatus.BREACHED

    db.commit()
    db.refresh(transfer)
    return transfer
