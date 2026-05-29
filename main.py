from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.connection import create_tables
from src.adapters.api.impression_router import router as impression_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando aplicação...")

    create_tables()

    print("✅ Banco conectado e tabelas verificadas!")

    yield

    print("🛑 Encerrando aplicação...")


app = FastAPI(
    title="Grêmio IFRN - Sistema de Impressões",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://gremio-ifrn-frontend-wktf.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(impression_router)


@app.get("/health")
def health():
    return {"status": "ok"}
