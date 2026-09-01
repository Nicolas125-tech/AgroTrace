from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.domain.models import CustodyStatus
from src.services.custody_service import initiate_transfer, resolve_quarantined_transfer
from src.db.session import get_db

router = APIRouter()

@router.post("/api/shipments/{id}/handshake/initiate")
def scan_qr_code(id: int, db: Session = Depends(get_db)):
    """Called by the warehouse scanner to receive the physical cargo."""
    try:
        transfer = initiate_transfer(db, shipment_id=id)
        return {"status": "success", "transfer_id": transfer.id, "transfer_status": transfer.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

from pydantic import BaseModel
from src.core.security import verify_password, generate_tenant_token
from src.domain.models import Tenant

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/api/auth/login")
def login_tenant(payload: LoginRequest, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.username == payload.username).first()
    if not tenant or not verify_password(payload.password, tenant.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = generate_tenant_token(tenant.id, tenant.role.value)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/api/admin/transfers/{transfer_id}/resolve")
def resolve_quarantined(transfer_id: int, force_status: CustodyStatus, db: Session = Depends(get_db)):
    """Manual audit resolution for Quarantined shipments."""
    try:
        transfer = resolve_quarantined_transfer(db, transfer_id, force_status)
        return {"status": "success", "new_status": transfer.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/shipments/{id}")
def get_shipment(id: int, db: Session = Depends(get_db)):
    from src.services.dashboard_service import get_shipment_details
    details = get_shipment_details(db, id)
    if not details:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return details

@router.get("/api/shipments/{id}/telemetry")
def get_shipment_telemetry(id: int, bucket_interval: str = "5 minutes", db: Session = Depends(get_db)):
    from src.services.dashboard_service import get_telemetry_downsampled
    return get_telemetry_downsampled(db, id, bucket_interval)

@router.get("/api/shipments/{id}/route")
def get_shipment_route(id: int, bucket_interval: str = "15 minutes", db: Session = Depends(get_db)):
    from src.services.dashboard_service import get_simplified_route
    return get_simplified_route(db, id, bucket_interval)

from pydantic import BaseModel
from src.core.security import generate_signed_token, verify_signed_token

class PublicShipmentView(BaseModel):
    id: int
    status: str
    tenant_id: int

@router.post("/api/shipments/{id}/generate-qr")
def generate_qr_url(id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    token = generate_signed_token(id, shipment.tenant_id)
    return {"url": f"https://agrotrace.com/handshake?token={token}", "token": token}

@router.get("/api/public/handshake", response_model=PublicShipmentView)
def public_handshake_view(token: str, db: Session = Depends(get_db)):
    try:
        # Max age: 24h = 86400 segundos
        payload = verify_signed_token(token, max_age=86400)
        shipment_id = payload["shipment_id"]
        tenant_id = payload["tenant_id"]
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
        
    # Injetando o Tenant do Token para o RLS liberar a leitura pública sem login do motorista
    from sqlalchemy import text
    db.execute(text("SELECT set_config('app.current_tenant', :tenant_id, true)"), {"tenant_id": str(tenant_id)})
    
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    return PublicShipmentView(
        id=shipment.id,
        status=shipment.status.value,
        tenant_id=shipment.tenant_id
    )

from datetime import datetime
from typing import Optional

class EphemeralDriverPayload(BaseModel):
    driver_cpf: str
    driver_name: str
    vehicle_plate: str
    offline_timestamp: Optional[datetime] = None

@router.post("/api/public/handshake")
def public_handshake_action(token: str, payload: EphemeralDriverPayload, db: Session = Depends(get_db)):
    try:
        token_data = verify_signed_token(token, max_age=86400)
        shipment_id = token_data["shipment_id"]
        tenant_id = token_data["tenant_id"]
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
        
    # Injetando Tenant Context (RLS Bypass for action)
    from sqlalchemy import text
    db.execute(text("SELECT set_config('app.current_tenant', :tenant_id, true)"), {"tenant_id": str(tenant_id)})
    
    from src.services.custody_service import initiate_transfer
    try:
        transfer = initiate_transfer(
            db, 
            shipment_id, 
            driver_cpf=payload.driver_cpf, 
            driver_name=payload.driver_name, 
            vehicle_plate=payload.vehicle_plate,
            offline_timestamp=payload.offline_timestamp
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"status": "success", "transfer_id": transfer.id, "custody_status": transfer.status.value}
