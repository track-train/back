# app/adapters/sqlalchemy/repositories/postgres.py
from ..models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

db_url = os.getenv("DATABASE_URL")

engine = create_engine(
    db_url
)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

def get_session():
    return Session()
