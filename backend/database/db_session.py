from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.constants import DATABASE_URL

# Second arg is for sqlite specifically - FastAPI uses multithreading by default.
# This ensures other threads can access the connection.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory: calling SessionLocal() gives you a new database session
# bound to the engine. Each session manages queries, transactions, and commits.
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session and ensure it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
