from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings

from src.api.routes import router
from src.db.session import engine
from src.domain.models import Base

# Criando as tabelas no TimescaleDB (apenas para dev; futuramente usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgroTrace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
