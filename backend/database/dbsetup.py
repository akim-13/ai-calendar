from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.misc.config import DATABASE_URL

# Second arg is for sqlite specifically - FastAPI uses multithreading on default
# This ensures other threads can access the connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create Object Relation Mapping (ORM) base for classes to inherit from
ORM_Base = declarative_base()

# Need to explicitly call db.commit()
# Flush means reload
# All sessions use the engine provided
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # This is known as a session factory
