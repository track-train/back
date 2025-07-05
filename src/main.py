from fastapi import FastAPI
from src.entrypoints.api.routers.profile import router as profile_router

app = FastAPI(title="API Hexagonale")
app.include_router(profile_router)