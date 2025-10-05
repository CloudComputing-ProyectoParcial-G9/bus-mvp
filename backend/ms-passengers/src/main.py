from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import passengers
from .config import start_db
from .seed_data import seed_passengers

app = FastAPI(title="ms-passengers")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(passengers.router, prefix="/api/v1", tags=["Passengers"])


@app.on_event("startup")
def on_startup():
    start_db()
    seed_passengers()


@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}
