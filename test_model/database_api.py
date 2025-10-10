from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import List
from datetime import datetime
import json

class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    task_id: int
    start: datetime
    end: datetime
    priority: int 
    tag: str
    
    @model_validator(mode="after")
    def check_time(self):
        if self.start >= self.end:
            raise ValueError("Event start time must be before end time")
        return self
    
class EventList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: List[Event]
    
    @field_validator('events')
    @classmethod
    def unique_ids(cls, even_list: List[Event]) -> List[Event]:
        ids = [event.id for event in even_list]
        if len(ids) != len(set(ids)):
            raise ValueError("Event IDs must be unique")
        return even_list
    
with open("test_model/database.json", encoding="utf-8") as f:
    database_raw = json.load(f)
    
events = EventList(events=database_raw)