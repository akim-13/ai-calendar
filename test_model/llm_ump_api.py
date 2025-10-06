from pydantic import BaseModel, ConfigDict 
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, time 
import json

class llmModel(BaseModel):
    model_config = ConfigDict(extra="forbid") # Raise error if extra fields are presented by llm
    
    task_name: str
    task_tag: str
    task_length_min: int 
    
    scope_start: datetime # ISO format string
    scope_end: datetime # ISO format string
    
    priority: int = 0 # from 0 to 2, where 0 is low, 1 is medium, 2 is high
    hours_per_day: int = 2
    spread: str = "evenly" # evenly/asap
    
    day_period_start: Optional[time] = None # time given by llm
    day_period_end: Optional[time] = None # time given by llm
    relation_to_day_period: Optional[str] = None # before/after/around
    
    another_task_mentioned: Optional[str] = None # name of another task mentioned
    number_of_another_task_mentioned: Optional[int] = None
    relation_to_another_task_mentioned: Optional[str] = None # before/after/around

class umpModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    allowed_weekdays: List[int]
    min_session_hours: Decimal = Decimal("0.5")
    max_session_hours: int = 2
    break_between_sessions_hours: Decimal = Decimal("0.25")
    
    sleep_start: time = time(23, 0)
    sleep_end:   time = time(7, 0)
    
    do_not_disturb_start: time = time(9, 0)
    do_not_disturb_end:   time = time(12, 0)
    
    preferred_hours_start: time = time(12, 0)
    preferred_hours_end:   time = time(20, 0)  
    
    
with open("test_model/llm.json", encoding="utf-8") as f:
    llm_raw = json.load(f)
llm_data = llmModel.model_validate(llm_raw)

with open("test_model/ump.json", encoding="utf-8") as f:
    ump_raw = json.load(f)
ump_data = umpModel.model_validate(ump_raw)
    
    
    