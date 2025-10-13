from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class EventBase(BaseModel):
    start: datetime
    end: datetime


class EventSchema(EventBase):
    id: int
    task_id: Optional[int] = None

    class Config:
        orm_mode = True


class EventCreateRequest(EventBase):
    task_id: Optional[int] = None


class TaskEventUpdate(BaseModel):
    start: datetime
    end: datetime
