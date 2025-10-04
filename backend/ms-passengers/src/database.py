import os
from sqlmodel import SQLModel, create_engine, Session
from urllib.parse import quote_plus

# Load .env file if present (helps with local dev and docker-compose .env)
try:
    from dotenv import load_dotenv
    # load .env in the repository root or current working dir if present
    load_dotenv()
except Exception:
    # python-dotenv is optional for runtime; tests don't require it
    pass

# Priority: SQL1_URL -> DATABASE_URL -> constructed from SQL1_* env vars -> sqlite fallback
DATABASE_URL = (
    os.environ.get("SQL1_URL")
    or os.environ.get("DATABASE_URL")
)

if not DATABASE_URL:
    sql1_host = os.environ.get("SQL1_HOST")
    sql1_port = os.environ.get("SQL1_PORT")
    sql1_db = os.environ.get("SQL1_DB")
    sql1_user = os.environ.get("SQL1_USER")
    sql1_password = os.environ.get("SQL1_PASSWORD")

    if sql1_host and sql1_db and sql1_user:
        # Build a Postgres URL. If password contains special chars, quote it.
        pwd = quote_plus(sql1_password) if sql1_password else ""
        port = sql1_port or "5432"
        DATABASE_URL = f"postgresql+psycopg2://{sql1_user}:{pwd}@{sql1_host}:{port}/{sql1_db}"
    else:
        # Fallback to local sqlite for dev/tests
        DATABASE_URL = os.environ.get("TEST_SQL1_URL") or "sqlite:///./dev_passengers.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

# Ensure tables exist. Tests using TestClient may not trigger the FastAPI startup event,
# so create tables at import time to make the test environment reliable.
def start_db():
    SQLModel.metadata.create_all(engine)

# Create tables immediately to support test clients that don't run startup handlers.
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
