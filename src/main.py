from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.entrypoints.api.routers.profile import router as profile_router
from src.entrypoints.api.routers.group import router as group_router
from src.entrypoints.api.routers.exercise import router as exercise_router
from src.entrypoints.api.routers.training import router as training_router
from src.entrypoints.api.routers.diet import router as diet_router


app = FastAPI(
    title="API Hexagonale",
    version="0.1.0",
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
    "http://localhost:8000",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "https://pre-prod.trackntrain.fr",
    "https://trackntrain.fr"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router)
app.include_router(group_router)
app.include_router(exercise_router)
app.include_router(training_router)
app.include_router(diet_router)



