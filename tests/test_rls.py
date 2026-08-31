import pytest
from sqlalchemy import text
from src.domain.models import Shipment, CargoProfile, Base
from src.db.session import engine, tenant_context
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def rls_db_session():
    # Bypass RLS context para o setup
    tenant_context.set(None)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    tenant_context.set(None)
    Base.metadata.drop_all(bind=engine)

def test_tenant_data_isolation(rls_db_session):
    # Injeta perfil público no banco (sem RLS)
    profile = CargoProfile(name="Global", max_temp=5, min_temp=0, continuous_exposure_limit_minutes=15)
    rls_db_session.add(profile)
    rls_db_session.commit()
    
    # ----------------------------------------------------
    # Simula requisição da Transportadora A (Tenant 1)
    # ----------------------------------------------------
    tenant_context.set(1)
    session_t1 = TestingSessionLocal()
    
    shipment1 = Shipment(tenant_id=1, profile_id=profile.id, grace_period_hours=2)
    session_t1.add(shipment1)
    session_t1.commit()
    session_t1.close()
    
    # ----------------------------------------------------
    # Simula requisição da Transportadora B (Tenant 2)
    # ----------------------------------------------------
    tenant_context.set(2)
    session_t2 = TestingSessionLocal()
    
    shipment2 = Shipment(tenant_id=2, profile_id=profile.id, grace_period_hours=2)
    session_t2.add(shipment2)
    session_t2.commit()
    session_t2.close()
    
    # ----------------------------------------------------
    # VERIFICAÇÃO DO SEAM 1: O Isolamento de Dados
    # O Tenant 1 NÃO usará .filter_by(tenant_id=1).
    # O Row-Level Security do TimescaleDB DEVE blindar os dados.
    # ----------------------------------------------------
    tenant_context.set(1)
    session_t1_verify = TestingSessionLocal()
    t1_shipments = session_t1_verify.query(Shipment).all() # Query PERIGOSA global
    
    assert len(t1_shipments) == 1, "RLS falhou: vazou dados da Transportadora B para a Transportadora A"
    assert t1_shipments[0].tenant_id == 1
    session_t1_verify.close()
    
    tenant_context.set(2)
    session_t2_verify = TestingSessionLocal()
    t2_shipments = session_t2_verify.query(Shipment).all() # Query PERIGOSA global
    
    assert len(t2_shipments) == 1, "RLS falhou: vazou dados da Transportadora A para a Transportadora B"
    assert t2_shipments[0].tenant_id == 2
    session_t2_verify.close()
