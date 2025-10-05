from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from enum import Enum

class PassengerStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class DocumentType(str, Enum):
    DNI = "DNI"
    PASSPORT = "PASSPORT"
    CE = "CE"

class Passenger(SQLModel, table=True):
    passenger_id: Optional[str] = Field(default=None, primary_key=True)
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    registration_date: Optional[str] = None
    status: Optional[str] = "active"
