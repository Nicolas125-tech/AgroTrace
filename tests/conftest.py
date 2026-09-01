import os
import pytest

os.environ['SECRET_KEY'] = 'test-secret-key-123'
os.environ['POSTGRES_PASSWORD'] = 'fake'

# We mock engine before main is imported to avoid hitting Postgres
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.event as event

DB_URL = "sqlite:///:memory:"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import src.db.session
src.db.session.engine = engine
src.db.session.SessionLocal = TestingSessionLocal

from src.domain.models import Base, Telemetry, Shipment

# Remove event listeners to avoid execution of PG specific queries on sqlite
event.remove(Telemetry.__table__, "after_create", src.domain.models.hypertable_ddl)
event.remove(Shipment.__table__, "after_create", src.domain.models.shipments_rls_ddl)

from main import app

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
