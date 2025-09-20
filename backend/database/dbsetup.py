from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.misc.config import DATABASE_URL

# Create PostgreSQL engine
engine = create_engine(DATABASE_URL)

# Create Object Relation Mapping (ORM) base for classes to inherit from
ORM_Base = declarative_base()

# Need to explicitly call db.commit()
# Flush means reload
# All sessions use the engine provided
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # This is known as a session factory
