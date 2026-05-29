import os
from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.connection import create_tables
from src.web.api.impression_router import router as impression_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.environ["TZ"] = "America/Fortaleza"

    if hasattr(os, "tzset"):
        os.tzset()

    create_tables()

    yield
    
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
