# Ignore unused imports.
# flake8: noqa: F401

from typing import Annotated as _Annotated

from fastapi import Depends as _Depends

# NOTE: Do not import from here in other files.
from sqlalchemy.orm import Session as _Session

from backend.database.db_session import get_db as _get_db
from backend.database.models.base import ORMBase
from backend.database.models.external_calendar import ExternalCalendar
from backend.database.models.plannable_attributes import PlannableTag, Recurrence, Tag
from backend.database.models.plannables import Event, Plannable, Task
from backend.database.models.user import User, UserModelParameters, UserSettings

DBSession = _Annotated[_Session, _Depends(_get_db)]

# NOTE: Public API - in other files import only these.
__all__ = [
    "ORMBase",
    "ExternalCalendar",
    "PlannableTag",
    "Recurrence",
    "Tag",
    "Event",
    "Plannable",
    "Task",
    "User",
    "UserModelParameters",
    "UserSettings",
    "DBSession",
]
