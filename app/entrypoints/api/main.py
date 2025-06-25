from fastapi import FastAPI

# on crée l'instance ASGI nommée "app"
app = FastAPI(
    title="TrackNTrain API",
    description="Exemple d'API hexagonale avec FastAPI",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur TrackNTrain !"}
