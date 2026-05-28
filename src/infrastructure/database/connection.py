from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.infrastructure.database.models import Base


# Configuração do PostgreSQL Neon
PGHOST = "ep-hidden-surf-aqhlliwz-pooler.c-8.us-east-1.aws.neon.tech"
PGDATABASE = "neondb"
PGUSER = "neondb_owner"
PGPASSWORD = "npg_ytPon5AjH6KT"
PGSSLMODE = "require"

# URL de conexão
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{PGUSER}:{PGPASSWORD}@"
    f"{PGHOST}/{PGDATABASE}"
    f"?sslmode={PGSSLMODE}"
)

# Cria engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Cria sessão
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


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


def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Testa conexão ao iniciar
test_connection()