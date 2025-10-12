from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.constants import DATABASE_URL

engine = create_engine(DATABASE_URL)

# Session factory: calling SessionLocal() gives you a new database session
# bound to the engine. Each session manages queries, transactions, and commits.
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session and automatically commit/rollback and close it.
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
