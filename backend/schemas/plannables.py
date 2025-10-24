from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class PlannableType(str, Enum):
    TASK = "task"
    EVENT = "event"

class PlannableSchema(BaseModel):
    id: int
    username: str
    type: str
    title: str
    is_completed: bool
    description: Optional[str]
    external_calendar_id: Optional[int]

    class Config:
        orm_mode = True
