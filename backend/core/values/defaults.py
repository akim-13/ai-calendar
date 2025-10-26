from dataclasses import dataclass

from backend.core.values.user_settings import Theme


@dataclass(frozen=True)
class DefaultUserSettings:
    timezone: str = "Europe/London"
    theme: Theme = Theme.LIGHT
