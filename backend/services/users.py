from sqlalchemy.orm import Session

from backend.database import User


def create_user(db: Session, username: str) -> User:
    """Create a new user account."""
    user = User(username=username)
    # TODO: Error handling (e.g., user already exists).
    # validate_new_user(db, user)
    db.add(user)
    db.flush()
    return user
