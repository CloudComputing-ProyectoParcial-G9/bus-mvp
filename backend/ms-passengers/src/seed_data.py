"""
Seed data for passengers database
This script populates the database with 10 sample passengers
"""
from datetime import datetime, timedelta
from sqlmodel import Session, select
from .database import engine
from .models import Passenger
import random


def generate_seed_passengers():
    """Generate 10 sample passengers"""
    
    # Sample data for generating realistic passengers
    first_names = ["Carlos", "María", "Juan", "Ana", "Luis", "Carmen", "José", "Isabel", "Miguel", "Laura"]
    last_names = ["García", "Rodríguez", "Martínez", "López", "González", "Hernández", "Pérez", "Sánchez", "Ramírez", "Torres"]
    
    passengers = []
    
    for i in range(1, 11):
        first_name = first_names[i-1]
        last_name = last_names[i-1]
        
        # Generate birth date (between 18 and 70 years old)
        age_years = random.randint(18, 70)
        birth_date = datetime.now() - timedelta(days=age_years*365 + random.randint(0, 365))
        
        # Generate registration date (within last 2 years)
        reg_days_ago = random.randint(1, 730)
        registration_date = datetime.now() - timedelta(days=reg_days_ago)
        
        # Document types and numbers
        doc_types = ["DNI", "PASSPORT", "CE"]
        doc_type = random.choice(doc_types)
        
        if doc_type == "DNI":
            doc_number = f"{random.randint(10000000, 99999999)}"
        elif doc_type == "PASSPORT":
            doc_number = f"{chr(random.randint(65, 90))}{random.randint(1000000, 9999999)}"
        else:  # CE
            doc_number = f"CE{random.randint(100000, 999999)}"
        
        passenger = Passenger(
            passenger_id=f"PASS{i:03d}",
            full_name=f"{first_name} {last_name}",
            email=f"{first_name.lower()}.{last_name.lower()}@email.com",
            phone=f"+34{random.randint(600000000, 799999999)}",
            document_type=doc_type,
            document_number=doc_number,
            date_of_birth=birth_date.strftime("%Y-%m-%d"),
            registration_date=registration_date.strftime("%Y-%m-%d"),
            status="active" if random.random() > 0.1 else "inactive"  # 90% active
        )
        passengers.append(passenger)
    
    return passengers


def seed_passengers():
    
    with Session(engine) as session:
        # Check if database is already populated
        statement = select(Passenger)
        existing_passengers = session.exec(statement).first()
        
        if existing_passengers:
            print("✓ Database already contains passengers. Skipping seed.")
            return
        
        print("📦 Seeding database with sample passengers...")
        
        passengers = generate_seed_passengers()
        
        for passenger in passengers:
            session.add(passenger)
        
        session.commit()
        
        print(f"✓ Successfully seeded database with {len(passengers)} passengers")
        print("\nSample passengers:")
        for p in passengers[:3]:
            print(f"  - {p.passenger_id}: {p.full_name} ({p.email})")
        print(f"  ... and {len(passengers)-3} more")


if __name__ == "__main__":
    # Allow running this script directly for manual seeding
    seed_passengers()
