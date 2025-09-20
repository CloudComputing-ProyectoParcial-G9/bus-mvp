from .database import start_db

def start_db_wrapper():
    start_db()

# kept for backwards compatibility
start_db = start_db
