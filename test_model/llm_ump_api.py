from pydantic import BaseModel, ConfigDict 
from typing import List, Optional, Annotated
from decimal import Decimal
from datetime import datetime, time 
import json

priority = Annotated[int, Field(ge=0, le=2)] # from 0 to 2, where 0 is low, 1 is medium, 2 is high
spread = Annotated[str, Field(regex="^(evenly|asap)$")] # evenly/asap 
relation_to_day_period_class = Annotated[Optional[str], Field(regex="^(before|after|around)?$")] 
relation_to_another_task_mentioned_class = Annotated[Optional[str], Field(regex="^(before|after|around)?$")]


class UserPromt(BaseModel):
    model_config = ConfigDict(extra="forbid") # Raise error if extra fields are presented by llm
    
    title: str
    tag: str
    task_length_minuntes: int 
    
    scope_start: datetime # ISO format string
    scope_end: datetime # ISO format string
    
    priority: priority 
    max_allowed_hours_per_day: int = 2 # max hours per day to spend on this task
    spread: str = "evenly" # evenly/asap (make it only being evenly or asap)
    
    day_period_start: Optional[time] = None # time given by llm
    day_period_end: Optional[time] = None # time given by llm
    relation_to_day_period: relation_to_day_period_class = None # before/after/around
    
    another_task_mentioned: Optional[str] = None # name of another task mentioned
    number_of_another_task_mentioned: Optional[int] = None
    relation_to_another_task_mentioned: relation_to_another_task_mentioned_class = None # before/after/around

class Ump(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    allowed_weekdays: List[int]
    min_session_hours: Decimal = Decimal("0.5")
    max_session_hours: Decimal = Decimal("2.0")
    min_break_between_sessions_hours: Decimal = Decimal("0.5")
    
    sleep_periost_start: time = time(23, 0)
    sleep_periost_end:   time = time(7, 0)  
    
    do_not_disturb_start: Optional[time] = None
    do_not_disturb_end:   Optional[time] = None
    
    preferred_hours_start: time = time(12, 0)
    preferred_hours_end:   time = time(20, 0)  
    
    
with open("test_model/llm.json", encoding="utf-8") as f:
    llm_raw = json.load(f)
llm_data = UserPromt.model_validate(llm_raw)

with open("test_model/ump.json", encoding="utf-8") as f:
    ump_raw = json.load(f)
ump_data = Ump.model_validate(ump_raw)
    
    
    