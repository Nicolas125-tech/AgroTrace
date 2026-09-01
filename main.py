import os

from fastapi import FastAPI

from src.api.routes import router
from src.db.session import engine
from src.domain.models import Base

# Criando as tabelas no TimescaleDB (apenas para dev; futuramente usar Alembic)
try:
    if os.getenv("TESTING") != "true":
        Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(title="AgroTrace API")

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
