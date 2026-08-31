import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, event, DDL
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ShipmentStatus(str, enum.Enum):
    IN_TRANSIT = "in_transit"
    IN_TRANSIT_OFFLINE = "in_transit_offline"
    BREACHED = "breached"
    DELIVERED = "delivered"

class CustodyStatus(str, enum.Enum):
    PENDING_SYNC = "pending_sync"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"

class CargoProfile(Base):
    __tablename__ = "cargo_profiles"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    max_temp = Column(Integer, nullable=False)
    min_temp = Column(Integer, nullable=False)
    continuous_exposure_limit_minutes = Column(Integer, nullable=False)

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("cargo_profiles.id"), nullable=False)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.IN_TRANSIT, nullable=False)
    grace_period_hours = Column(Integer, nullable=False)

class CustodyTransfer(Base):
    __tablename__ = "custody_transfers"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    status = Column(Enum(CustodyStatus), default=CustodyStatus.PENDING_SYNC, nullable=False)
    initiated_at = Column(DateTime, nullable=False)
    driver_cpf = Column(String, nullable=True)
    driver_name = Column(String, nullable=True)
    vehicle_plate = Column(String, nullable=True)

class Telemetry(Base):
    __tablename__ = "telemetry"
    # TimescaleDB requires the partition column (timestamp) to be part of the primary key
    timestamp = Column(DateTime, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), primary_key=True)
    temperature = Column(Integer, nullable=False)
    humidity = Column(Integer, nullable=True)
    gps = Column(String, nullable=True)

# SQLAlchemy DDL hook to turn telemetry into a TimescaleDB hypertable
# 'if_not_exists' ensures idempotency if created multiple times
hypertable_ddl = DDL(
    "SELECT create_hypertable('telemetry', 'timestamp', if_not_exists => TRUE);"
)
event.listen(Telemetry.__table__, "after_create", hypertable_ddl)

shipments_rls_ddl = DDL("""
    ALTER TABLE shipments ENABLE ROW LEVEL SECURITY;
    ALTER TABLE shipments FORCE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS tenant_isolation_policy ON shipments;
    CREATE POLICY tenant_isolation_policy ON shipments
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true)::integer)
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true)::integer);
""")
event.listen(Shipment.__table__, "after_create", shipments_rls_ddl)
