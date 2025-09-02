from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
import os

from dotenv import load_dotenv
from src.adapters.sqlalchemy.db import create_tables

load_dotenv()
print("DEBUG ENV =", os.getenv("ENV"))
print("DEBUG DATABASE_URL =", os.getenv("DATABASE_URL"))
app = FastAPI()
from src.adapters.scheduler.daily_notification import start_daily_notification_scheduler

from src.entrypoints.api.routers.profile import router as profile_router
from src.entrypoints.api.routers.group import router as group_router
from src.entrypoints.api.routers.exercise import router as exercise_router
from src.entrypoints.api.routers.training import router as training_router
from src.entrypoints.api.routers.diet import router as diet_router
from src.entrypoints.api.routers.daily_checkup import router as daily_checkup_router
from src.entrypoints.api.routers.notification import router as notification_router


bearer_scheme = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="TracknTrain",
        version="0.7.0",
        description="API For TracknTrain",
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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
app.include_router(daily_checkup_router)
app.include_router(notification_router)

@app.on_event("startup")
async def startup_event():
    await create_tables()
    print("[APP] FastAPI startup, launching scheduler...")
    start_daily_notification_scheduler()
