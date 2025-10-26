import zoneinfo
from datetime import datetime

from sqlalchemy.orm import Session

from backend.core.entities import User
from backend.core.values.defaults import DefaultUserSettings
from backend.shared.utils.time_defaults import get_valid_or_default_timezone


def create_user(db: Session, username: str) -> User:
    """Create a new user account."""
    user = User(username=username)
    # TODO: Error handling (e.g., user already exists).
    # validate_new_user(db, user)
    db.add(user)
    db.flush()
    return user


def get_user_timezone(user: User) -> zoneinfo.ZoneInfo:
    """Return the user's timezone, fall back to the default if unset."""
    timezone_name = (
        user.settings.timezone
        if user.settings and user.settings.timezone
        else DefaultUserSettings.timezone
    )

    return get_valid_or_default_timezone(timezone_name)


def get_current_user_time(user: User) -> datetime:
    """Return the current datetime localized to the user's timezone."""
    return datetime.now(get_user_timezone(user))
