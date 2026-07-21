from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator

from src.infrastructure.database.models import Base

PGHOST = "ep-hidden-surf-aqhlliwz-pooler.c-8.us-east-1.aws.neon.tech"
PGDATABASE = "neondb"
PGUSER = "neondb_owner"
PGPASSWORD = "npg_ytPon5AjH6KT"

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{PGUSER}:{PGPASSWORD}@"
    f"{PGHOST}/{PGDATABASE}"
    f"?ssl=require"
)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


async def test_connection():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            print("✅ Conectado ao PostgreSQL Neon com sucesso!")
    except Exception as e:
        print("❌ Erro ao conectar no banco:")
        print(e)


async def create_tables():
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print("❌ Erro ao criar tabelas:")
        print(e)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
