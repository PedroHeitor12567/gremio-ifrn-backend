from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.connection import create_tables, get_session
from src.web.api.impression_router import router as impression_router
from src.web.api.auth_router import router as auth_router
from src.application.use_cases.auth_use_cases import SeedAdminUseCase
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    async for session in get_session():
        try:
            await SeedAdminUseCase(SQLAlchemyUserRepository(session)).execute()
        finally:
            await session.close()
    yield


app = FastAPI(
    title="Grêmio IFRN - Sistema de Impressões",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(impression_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
