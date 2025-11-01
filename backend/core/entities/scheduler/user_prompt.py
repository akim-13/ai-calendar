from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from typing import List
from datetime import datetime, time
from core.entities.scheduler import Tick
from core.values.enums import Priority, Spread, Relation


class UserPrompt(BaseModel):
    # Raise error if extra fields are presented by llm
    model_config = ConfigDict(extra="forbid") 
    
    title: str
    tag: str
    task_length_hours: int 

    # ISO format strings.
    scope_start: datetime 
    scope_end: datetime
    
    priority: Priority
    max_allowed_hours_per_day: int = 2 # max hours per day to spend on this task
    spread: Spread = Spread.UNIFORM
    
    day_period_start: time | None = None  # time given by llm
    day_period_end: time | None = None  # time given by llm
    relation_to_day_period: Relation | None = None

    another_task_mentioned: str | None = None  # name of another task mentioned
    number_of_another_task_mentioned: int | None = None
    relation_to_another_task_mentioned: Relation | None = None
    
    @field_validator('day_period_start', 'day_period_end', 'relation_to_day_period', 
                     'another_task_mentioned', 'relation_to_another_task_mentioned', mode='before')
    @classmethod
    def empty_str_to_none(cls, value):
        """Convert empty strings to None for optional fields"""
        if value == '':
            return None
        return value

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
    def scope_start_tick(self) -> int:  
        """Scope start is always tick 0 (after rounding)"""
        return 0  
    
    @computed_field
    @property
    def scope_end_tick(self) -> int:  
        """Convert scope_end datetime to Tick (relative to rounded scope_start = 0)"""
        return int(Tick.from_datetime_diff(self.scope_end_rounded, self.scope_start_rounded))  
    
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
    
    @computed_field
    @property
    def get_day_period_ticks(self) -> List[int]:
        """Get day period ticks for the entire scope"""
        if self.day_period_start is None or self.day_period_end is None:
            return []
        return Tick.time_window_to_list_of_ticks(
            self.day_period_start,
            self.day_period_end,
            self.scope_start_rounded,
            self.scope_end_rounded
        )
