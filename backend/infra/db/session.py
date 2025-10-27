from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from infra.db.constants import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# NOTE: Do not import anything from here. Only import DBSession from `__init__.py`.

_engine = create_engine(DATABASE_URL)
_SessionLocal = sessionmaker(bind=_engine)


def _get_db() -> Generator[Session, None, None]:
    """
    Provide a database session and automatically commit/rollback and close it.
    """
    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DBSession = Annotated[Session, Depends(_get_db)]
