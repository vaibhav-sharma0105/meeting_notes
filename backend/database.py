from sqlmodel import SQLModel, create_engine, Session
import os

# Default to a local postgres url if not set
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/meetops")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    # Note: pgvector extension must be enabled in the DB: CREATE EXTENSION vector;
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
