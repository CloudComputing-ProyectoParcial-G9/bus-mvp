from fastapi import FastAPI
from routes import passengers
from config import start_db

app = FastAPI(title="ms-passengers")

app.include_router(passengers.router, prefix="", tags=["Passengers"]) 


@app.on_event("startup")
def on_startup():
    start_db()


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}
