from sqlalchemy.orm import Session
from backend.database import User
from sqlalchemy.exc import IntegrityError
from backend.database.models.user import UserSettings


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

def update_user(db, request):
    """Update user fields. Returns None if user not found, else updated user"""
    user = db.query(User).filter(User.username == request.username).first()
    if user is None:
        return None
    if request.last_login is not None:
        user.last_login = request.last_login
    if request.is_active is not None:
        user.is_active = request.is_active

    if request.timezone is not None :
        if user.settings is None:
            user.settings = UserSettings(username=user.username, timezone=request.timezone, theme=request.theme or "light")
        else:
            user.settings.timezone = request.timezone
    if request.theme is not None:
        if user.settings is None:
            user.settings = UserSettings(username=user.username, timezone=request.timezone or "GMT", theme=request.theme)
        else:
            user.settings.theme = request.theme
    db.flush()
    return user


def delete_user(db: Session, username: str) -> User | None:
    """Delete a user account. Returns the user if username exists, else None"""
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        return None
    
    db.delete(user)
    db.flush()
    return user
    


