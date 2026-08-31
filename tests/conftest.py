import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models import Base

DB_URL = "postgresql+psycopg://agrotrace:agrotrace_dev@localhost:5432/agrotrace"
engine = create_engine(DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
