# app/adapters/sqlalchemy/repositories/postgres.py
from ..models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,      
    pool_size=10,   
    max_overflow=20
)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)


def get_session():
    return Session()
