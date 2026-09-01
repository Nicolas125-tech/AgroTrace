from contextvars import ContextVar

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings

tenant_context = ContextVar("tenant_id", default=None)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@event.listens_for(Session, "after_begin")
def set_tenant_context(session, transaction, connection):
    tenant_id = tenant_context.get()
    if tenant_id is not None:
        connection.execute(text("SELECT set_config('app.current_tenant', :tenant_id, true)"), {"tenant_id": str(tenant_id)})

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
