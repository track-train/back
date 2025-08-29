from src.adapters.sqlalchemy.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os

db_url = os.getenv("DATABASE_URL") or "postgresql://user:user@localhost:5432/postgres"

if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url,
    pool_size=20,
    max_overflow=20,
    pool_timeout=30,
)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

SessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    autocommit=False, 
    autoflush=False
)

async def get_async_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
