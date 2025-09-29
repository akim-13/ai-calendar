import zoneinfo
from datetime import datetime

from backend.misc.defaults import DefaultUserSettings
from backend.misc.logger import get_logger

log = get_logger(__name__)


def get_valid_or_default_timezone(timezone_name: str) -> zoneinfo.ZoneInfo:
    """Return ZoneInfo for name, fall back and log error if invalid."""
    try:
        return zoneinfo.ZoneInfo(timezone_name)
    except zoneinfo.ZoneInfoNotFoundError:
        log.error("Invalid timezone: %s", timezone_name)
        return zoneinfo.ZoneInfo(DefaultUserSettings.timezone)


def get_current_time_in_default_timezone() -> datetime:
    """Return the current datetime localised to the default timezone."""
    return datetime.now(get_valid_or_default_timezone(DefaultUserSettings.timezone))
