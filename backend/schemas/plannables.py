from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreatePlannableRequest(BaseModel):
    username: str
    external_calendar_id: Optional[int] = None
    type: str  # "task" or "event"
    title: str
    description: Optional[str] = None
    is_completed: Optional[bool] = False

class UpdatePlannableRequest(BaseModel):
    title: Optional[str]
    description: Optional[str]
    type: Optional[str]
    is_completed: Optional[bool]

class PlannableSchema(BaseModel):
    id: int
    username: str
    external_calendar_id: Optional[int]
    type: str
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
