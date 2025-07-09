# app/adapters/sqlalchemy/repositories/postgres.py
from src.adapters.sqlalchemy.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL") or "postgresql://user:user@localhost:5432/postgres"

engine = create_engine(
    db_url
)

Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

