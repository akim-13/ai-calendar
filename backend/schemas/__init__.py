from typing import TypeAlias as _TypeAlias

from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic as _sqlalchemy_to_pydantic

from backend.database import (
    Event,
    ExternalCalendar,
    Plannable,
    PlannableTag,
    Recurrence,
    Tag,
    Task,
    User,
    UserModelParameters,
    UserSettings,
)

# flake8: noqa: F403, F401
from backend.schemas.events import *
from backend.schemas.tasks import *
from backend.schemas.users import *

# NOTE: Use these in FastAPI's routers.
ExternalCalendarSchema: _TypeAlias = _sqlalchemy_to_pydantic(ExternalCalendar)  # type: ignore
PlannableTagSchema: _TypeAlias = _sqlalchemy_to_pydantic(PlannableTag)  # type: ignore
RecurrenceSchema: _TypeAlias = _sqlalchemy_to_pydantic(Recurrence)  # type: ignore
TagSchema: _TypeAlias = _sqlalchemy_to_pydantic(Tag)  # type: ignore
EventSchema: _TypeAlias = _sqlalchemy_to_pydantic(Event)  # type: ignore
PlannableSchema: _TypeAlias = _sqlalchemy_to_pydantic(Plannable)  # type: ignore
TaskSchema: _TypeAlias = _sqlalchemy_to_pydantic(Task)  # type: ignore
UserModelParametersSchema: _TypeAlias = _sqlalchemy_to_pydantic(UserModelParameters)  # type: ignore
UserSettingsSchema: _TypeAlias = _sqlalchemy_to_pydantic(UserSettings)  # type: ignore
