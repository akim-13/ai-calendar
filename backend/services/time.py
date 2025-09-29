import zoneinfo
from datetime import datetime

from backend.database import User
from backend.misc.defaults import DefaultUserSettings
from backend.tools.time_defaults import get_valid_or_default_timezone


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
