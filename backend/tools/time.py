import zoneinfo
from datetime import datetime

from backend.database import User
from backend.misc.defaults import DefaultUserSettings
from backend.misc.logger import get_logger

log = get_logger(__name__)


def get_users_timezone(user: User) -> zoneinfo.ZoneInfo:
    """Return the user's timezone, fall back to the default if unset."""
    timezone_name = (
        user.settings.timezone
        if user.settings and user.settings.timezone
        else DefaultUserSettings.timezone
    )

    return get_valid_or_default_timezone(timezone_name)


def get_valid_or_default_timezone(timezone_name: str) -> zoneinfo.ZoneInfo:
    """Return ZoneInfo for name, fall back and log error if invalid."""
    try:
        return zoneinfo.ZoneInfo(timezone_name)
    except zoneinfo.ZoneInfoNotFoundError:
        log.error("Invalid timezone: %s", timezone_name)
        return zoneinfo.ZoneInfo(DefaultUserSettings.timezone)


def get_users_current_time(user: User) -> datetime:
    """Return the current datetime localized to the user's timezone."""
    return datetime.now(get_users_timezone(user))


def get_current_time_in_default_timezone() -> datetime:
    """Return the current datetime localised to the default timezone."""
    return datetime.now(get_valid_or_default_timezone(DefaultUserSettings.timezone))
