from fastapi import Depends
from sqlalchemy.orm import Session
from src.adapters.sqlalchemy.db import SessionLocal
from typing import Generator

def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()