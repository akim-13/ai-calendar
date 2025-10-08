from sqlalchemy.orm import Session
from backend.database import User
from sqlalchemy.exc import IntegrityError
from schemas import UserSchema
from datetime import datetime


def create_user(db: Session, username: str) -> User | None:
    """Create and return new user account. Returns None if username exists."""
    user = User(username=username)
    db.add(user)
    try:
        db.flush()
        return user
    except IntegrityError:
        db.rollback()
        return None

def get_user(db: Session, username: str) -> User | None:
    """Delete a user account. Returns the user if username exists, else None"""
    user = db.query(User).filter(User.username == username).first()
    
    return user

# region User update services

def update_user_activity(db: Session, username: str, is_active: bool) -> datetime | None:
    """Update a user account. Returns None if username doesn't exist"""
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        return None
    
    user.is_active = is_active
    
    
def update_user_last_login(db: Session, username: str, last_login: datetime) -> datetime | None:
    """Update a user account. Returns None is username doesn't exist"""
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        return None
    
    user.last_login = last_login

# endregion


def delete_user(db: Session, username: str) -> User | None:
    """Delete a user account. Returns the user if username exists, else None"""
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        return None
    
    db.delete(user)
    db.flush()
    return user
    


