from datetime import datetime

from pydantic import BaseModel


class TaskEventUpdate(BaseModel):
    start: datetime
    end: datetime
