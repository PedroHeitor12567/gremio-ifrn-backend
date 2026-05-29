from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from src.infrastructure.database.models import Base

PGHOST = "ep-hidden-surf-aqhlliwz-pooler.c-8.us-east-1.aws.neon.tech"
PGDATABASE = "neondb"
PGUSER = "neondb_owner"
PGPASSWORD = "npg_ytPon5AjH6KT"
PGSSLMODE = "require"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{PGUSER}:{PGPASSWORD}@"
    f"{PGHOST}/{PGDATABASE}"
    f"?sslmode={PGSSLMODE}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("✅ Conectado ao PostgreSQL Neon com sucesso!")
    except Exception as e:
        print("❌ Erro ao conectar no banco:")
        print(e)


def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print("❌ Erro ao criar tabelas:")
        print(e)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


test_connection()