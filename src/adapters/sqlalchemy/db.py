# app/adapters/sqlalchemy/repositories/postgres.py
from src.adapters.sqlalchemy.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL") or "postgresql://user:user@localhost:5432/postgres"

# ✅ Convertir l'URL pour asyncpg
if db_url.startswith("postgresql://") and "asyncpg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# ✅ Moteur asynchrone
engine = create_async_engine(
    db_url,
    pool_size=20,
    max_overflow=20,
    pool_timeout=30,
    echo=False,  # Mettre True pour debug
)

# ✅ Factory de sessions asynchrones
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ✅ Fonction pour créer les tables (asynchrone)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ✅ Fonction pour obtenir une session
async def get_session():
    async with SessionLocal() as session:
        yield session

