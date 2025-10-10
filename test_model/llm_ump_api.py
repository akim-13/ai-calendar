from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field
from typing import List, Optional, Annotated
from decimal import Decimal
from datetime import datetime, time, timedelta
import json

class Tick:
    MINUTES_PER_TICK = 5
    
    def __init__(self, tick_number: int):
        self.tick_number = tick_number
        
    @staticmethod
    def round_datetime_to_tick_boundary(dt: datetime, round_up: bool = False) -> datetime:
        """Round datetime to nearest 5-minute boundary
        Args:
            round_up: if True, always round up; if False, round down
        """
        
        minutes = dt.minute
        seconds = dt.second
        microseconds = dt.microsecond
        
        if round_up and (seconds > 0 or microseconds > 0 or minutes % 5 != 0):
            # Round up to next 5-minute boundary
            remainder = minutes % 5
            minutes_to_add = (5 - remainder) if remainder != 0 else 0
            rounded = dt.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_add)
        else:
            # Round down to previous 5-minute boundary
            remainder = minutes % 5
            rounded = dt.replace(minute=minutes - remainder, second=0, microsecond=0)

        return rounded
    
    @classmethod
    def from_datetime_diff(cls, dt: datetime, reference_datetime: datetime) -> 'Tick':
        """Convert datetime to tick number relative to reference datetime"""
        minutes_since_reference = int((dt - reference_datetime).total_seconds() / 60)
        tick_number = minutes_since_reference // cls.MINUTES_PER_TICK
        return cls(tick_number)
    
    @classmethod
    def from_hours(cls, hours: float) -> int:
        """Convert hours to number of ticks"""
        return int((hours * 60) / cls.MINUTES_PER_TICK)
    
    @staticmethod
    def to_datetime(tick_number: int, reference_datetime: datetime) -> datetime:
        """Convert tick number back to datetime given a reference"""
        minutes = tick_number * Tick.MINUTES_PER_TICK
        return reference_datetime + timedelta(minutes=minutes)
    
    def __int__(self):
        return self.tick_number
    
    def __eq__(self, other):
        if isinstance(other, Tick):
            return self.tick_number == other.tick_number
        return False
        

priority_type = Annotated[int, Field(ge=0, le=2)] # from 0 to 2, where 0 is low, 1 is medium, 2 is high
spread_type = Annotated[str, Field(regex="^(evenly|asap)$")] # evenly/asap 
relation_to_day_period_type = Annotated[Optional[str], Field(regex="^(before|after|around)?$")] 
relation_to_another_task_mentioned_type = Annotated[Optional[str], Field(regex="^(before|after|around)?$")]


class UserPromt(BaseModel):
    model_config = ConfigDict(extra="forbid") # Raise error if extra fields are presented by llm
    
    title: str
    tag: str
    task_length_hours: int 
    
    scope_start: datetime # ISO format string
    scope_end: datetime # ISO format string
    
    priority: priority_type
    max_allowed_hours_per_day: int = 2 # max hours per day to spend on this task
    spread: spread_type = "evenly" # evenly/asap (make it only being evenly or asap)
    
    day_period_start: Optional[time] = None # time given by llm
    day_period_end: Optional[time] = None # time given by llm
    relation_to_day_period: relation_to_day_period_type = None # before/after/around
    
    another_task_mentioned: Optional[str] = None # name of another task mentioned
    number_of_another_task_mentioned: Optional[int] = None
    relation_to_another_task_mentioned: relation_to_another_task_mentioned_type = None # before/after/around
    
    @computed_field
    @property
    def scope_start_rounded(self) -> datetime:
        """Scope start rounded down to 5-minute boundary"""
        return Tick.round_datetime_to_tick_boundary(self.scope_start, round_up=False)
    
    @computed_field
    @property
    def scope_end_rounded(self) -> datetime:
        """Scope end rounded up to 5-minute boundary"""
        return Tick.round_datetime_to_tick_boundary(self.scope_end, round_up=True)
    
    # Computed fields that convert to ticks (using rounded scope_start as tick 0)
    @computed_field
    @property
    def task_length_ticks(self) -> int:
        """Convert task length from minutes to ticks"""
        return Tick.from_hours(self.task_length_hours)
    
    @computed_field
    @property
    def scope_start_tick(self) -> Tick:
        """Scope start is always tick 0 (after rounding)"""
        return Tick(0)
    
    @computed_field
    @property
    def scope_end_tick(self) -> Tick:
        """Convert scope_end datetime to Tick (relative to rounded scope_start = 0)"""
        return Tick.from_datetime_diff(self.scope_end_rounded, self.scope_start_rounded)
    
    @computed_field
    @property
    def max_allowed_ticks_per_day(self) -> int:
        """Convert max hours per day to ticks"""
        return Tick.from_hours(self.max_allowed_hours_per_day)
    
    @computed_field
    @property
    def scope_duration_ticks(self) -> int:
        """Calculate total ticks in the scope"""
        return int(self.scope_end_tick) - int(self.scope_start_tick)
    

class Ump(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    allowed_weekdays: List[int]
    min_session_hours: Decimal = Decimal("0.5")
    max_session_hours: Decimal = Decimal("2.0")
    min_break_between_sessions_hours: Decimal = Decimal("0.5")
    
    sleep_period_start: time = time(23, 0)
    sleep_period_end:   time = time(7, 0)
    
    do_not_disturb_start: Optional[time] = None
    do_not_disturb_end:   Optional[time] = None
    
    preferred_hours_start: time = time(12, 0)
    preferred_hours_end:   time = time(20, 0)
    
    @computed_field
    @property
    def min_session_ticks(self) -> int:
        """Convert min session hours to ticks"""
        return Tick.from_hours(float(self.min_session_hours))
    
    @computed_field
    @property
    def max_session_ticks(self) -> int:
        """Convert max session hours to ticks"""
        return Tick.from_hours(float(self.max_session_hours))
    
    @computed_field
    @property
    def min_break_ticks(self) -> int:
        """Convert min break hours to ticks"""
        return Tick.from_hours(float(self.min_break_between_sessions_hours))
    
    
with open("test_model/llm.json", encoding="utf-8") as f:
    llm_raw = json.load(f)
llm_data = UserPromt.model_validate(llm_raw)

with open("test_model/ump.json", encoding="utf-8") as f:
    ump_raw = json.load(f)
ump_data = Ump.model_validate(ump_raw)
    
    
    