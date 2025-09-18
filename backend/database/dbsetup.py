from datetime import datetime

from sqlalchemy import DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from backend.misc.config import DATABASE_URL


# All Object Relation Mapping (ORM) models must inherit from this base class.
class ORMBase(DeclarativeBase):
    pass


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamp columns to an ORM model.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


# Second arg is for sqlite specifically - FastAPI uses multithreading on default
# This ensures other threads can access the connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory: calling SessionLocal() gives you a new database session
# bound to the engine. Each session manages queries, transactions, and commits.
SessionLocal = sessionmaker(bind=engine)
