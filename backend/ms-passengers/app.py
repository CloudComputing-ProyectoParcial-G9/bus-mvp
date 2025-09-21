from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uuid

app = FastAPI()

class Passenger(BaseModel):
    id: str | None = None
    name: str
    email: str | None = None

# In-memory store
store: Dict[str, Passenger] = {}


@app.get('/health')
def health():
    return {"status": "healthy"}


@app.post('/passengers', status_code=201)
def create_passenger(p: Passenger):
    pid = p.id or f"pass_{uuid.uuid4().hex[:8]}"
    p.id = pid
    store[pid] = p
    return p


@app.get('/passengers/{passenger_id}')
def get_passenger(passenger_id: str):
    p = store.get(passenger_id)
    if not p:
        raise HTTPException(status_code=404, detail='Passenger not found')
    return p
