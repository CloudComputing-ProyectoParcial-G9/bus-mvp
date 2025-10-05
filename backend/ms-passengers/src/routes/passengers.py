from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlmodel import select, Session
from ..models import Passenger, PassengerStatus, DocumentType
from ..database import get_session
import uuid

router = APIRouter()

@router.get('/passengers', response_model=List[Passenger])
def list_passengers(
    page: int = 1, 
    limit: int = 20, 
    status: Optional[PassengerStatus] = None, 
    document_type: Optional[DocumentType] = None,
    search: str = None, 
    session: Session = Depends(get_session)
):
    query = select(Passenger)
    
    # Apply filters
    if status:
        query = query.where(Passenger.status == status.value)
    if document_type:
        query = query.where(Passenger.document_type == document_type.value)
    if search:
        query = query.where(
            (Passenger.full_name.contains(search)) | 
            (Passenger.email.contains(search))
        )
    
    results = session.exec(query.offset((page-1)*limit).limit(limit)).all()
    return results

@router.post('/passengers', status_code=201, response_model=Passenger)
def create_passenger(payload: Passenger, session: Session = Depends(get_session)):
    passenger = payload
    if not passenger.passenger_id:
        passenger.passenger_id = str(uuid.uuid4())
    # simple uniqueness check by email
    existing = session.exec(select(Passenger).where(Passenger.email == passenger.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Passenger with this email already exists")
    session.add(passenger)
    session.commit()
    session.refresh(passenger)
    return passenger

@router.get('/passengers/{passenger_id}', response_model=Passenger)
def get_passenger(passenger_id: str, session: Session = Depends(get_session)):
    passenger = session.get(Passenger, passenger_id)
    if not passenger:
        raise HTTPException(status_code=404, detail='Passenger not found')
    return passenger

@router.put('/passengers/{passenger_id}', response_model=Passenger)
def update_passenger(passenger_id: str, payload: Passenger, session: Session = Depends(get_session)):
    passenger = session.get(Passenger, passenger_id)
    if not passenger:
        raise HTTPException(status_code=404, detail='Passenger not found')
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(passenger, k, v)
    session.add(passenger)
    session.commit()
    session.refresh(passenger)
    return passenger

@router.delete('/passengers/{passenger_id}', status_code=204)
def delete_passenger(passenger_id: str, session: Session = Depends(get_session)):
    passenger = session.get(Passenger, passenger_id)
    if not passenger:
        raise HTTPException(status_code=404, detail='Passenger not found')
    session.delete(passenger)
    session.commit()
    return None
