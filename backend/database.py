from sqlmodel import SQLModel, create_engine, Session, text
import os
import time
import logging

# Default to a local postgres url if not set
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/meetops")

engine = create_engine(DATABASE_URL, echo=True)

logger = logging.getLogger("uvicorn")

def check_db_connection(max_retries=5, wait_seconds=2):
    """
    Attempts to connect to the database with retries.
    """
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful.")
            return True
        except Exception as e:
            logger.warning(f"Database connection failed (Attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(wait_seconds)

    return False

def create_db_and_tables():
    # Note: pgvector extension must be enabled in the DB: CREATE EXTENSION vector;
    # We attempt to enable it here if possible, though usually needs superuser
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    except Exception as e:
        logger.warning(f"Could not enable pgvector extension (might already exist or permission denied): {e}")

    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
