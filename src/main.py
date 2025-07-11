from fastapi import FastAPI
from fastapi.middleware import Middleware

from src.entrypoints.api.routers.profile import router as profile_router
from src.entrypoints.api.routers.group import router as group_router
from src.entrypoints.api.routers.exercise import router as exercise_router


app = FastAPI(
    title="API Hexagonale",
    version="0.1.0",
)


app.include_router(profile_router)
app.include_router(group_router)
app.include_router(exercise_router)



