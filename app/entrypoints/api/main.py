import os
from fastapi import FastAPI
from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
from app.adapters.sqlalchemy.models import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

# on crée l'instance ASGI nommée "app"
app = FastAPI(
    title="TrackNTrain API",
    description="Exemple d'API hexagonale avec FastAPI",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur TrackNTrain !"}
