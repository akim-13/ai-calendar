from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field, StringConstraints
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
    
    @staticmethod
    def time_window_to_list_of_ticks(period_start: time, period_end: time, 
                                      scope_start: datetime, scope_end: datetime) -> List[int]:
        """
        Convert a daily recurring time window to a list of tick numbers across the entire scope.
        
        Args:
            period_start: Start time of the daily period (e.g., 23:00)
            period_end: End time of the daily period (e.g., 07:00)
            scope_start: Tick 0
            scope_end: The end of the scope
            
        Returns:
            List of tick numbers that fall within the time window across all days
        """
        time_window_ticks = []
        
        # Round scope boundaries to tick boundaries
        scope_start_rounded = Tick.round_datetime_to_tick_boundary(scope_start, round_up=False)
        scope_end_rounded = Tick.round_datetime_to_tick_boundary(scope_end, round_up=True)
        
        # Calculate total days in scope 
        total_days = (scope_end_rounded.date() - scope_start_rounded.date()).days + 1
        
        # Handle overnight periods (when period_end < period_start, e.g., 23:00 to 07:00)
        spans_midnight = period_end < period_start
        
        # Generate ticks for each day in the scope
        for day_offset in range(total_days):
            current_date = scope_start_rounded.date() + timedelta(days=day_offset)
            
            if spans_midnight:
                # Split into two segments: [period_start -> midnight] and [midnight -> period_end]
                
                # Segment 1: period_start to end of day
                segment1_start = datetime.combine(current_date, period_start)
                segment1_end = datetime.combine(current_date, time(23, 59, 59))
                
                # Segment 2: start of next day to period_end
                next_date = current_date + timedelta(days=1)
                segment2_start = datetime.combine(next_date, time(0, 0, 0))
                segment2_end = datetime.combine(next_date, period_end)
                
                # Process both segments
                for segment_start, segment_end in [(segment1_start, segment1_end), 
                                                     (segment2_start, segment2_end)]:
                    # Only process if segment overlaps with scope
                    if segment_start < scope_end_rounded and segment_end >= scope_start_rounded:
                        # Clamp to scope boundaries
                        actual_start = max(segment_start, scope_start_rounded)
                        actual_end = min(segment_end, scope_end_rounded)
                        
                        # Round to tick boundaries
                        tick_start = Tick.round_datetime_to_tick_boundary(actual_start, round_up=False)
                        tick_end = Tick.round_datetime_to_tick_boundary(actual_end, round_up=True)
                        
                        # Convert to tick numbers
                        start_tick = Tick.from_datetime_diff(tick_start, scope_start_rounded).tick_number
                        end_tick = Tick.from_datetime_diff(tick_end, scope_start_rounded).tick_number
                        
                        # Add all ticks in this range
                        time_window_ticks.extend(range(start_tick, end_tick))
            else:
                # Simple case: period within same day
                period_start_dt = datetime.combine(current_date, period_start)
                period_end_dt = datetime.combine(current_date, period_end)
                
                # Only process if period overlaps with scope
                if period_start_dt < scope_end_rounded and period_end_dt >= scope_start_rounded:
                    # Clamp to scope boundaries
                    actual_start = max(period_start_dt, scope_start_rounded)
                    actual_end = min(period_end_dt, scope_end_rounded)
                    
                    # Round to tick boundaries
                    tick_start = Tick.round_datetime_to_tick_boundary(actual_start, round_up=False)
                    tick_end = Tick.round_datetime_to_tick_boundary(actual_end, round_up=True)
                    
                    # Convert to tick numbers
                    start_tick = Tick.from_datetime_diff(tick_start, scope_start_rounded).tick_number
                    end_tick = Tick.from_datetime_diff(tick_end, scope_start_rounded).tick_number
                    
                    # Add all ticks in this range
                    time_window_ticks.extend(range(start_tick, end_tick))
        
        return sorted(list(set(time_window_ticks)))
                                           
    
    def __int__(self):
        return self.tick_number
    
    def __eq__(self, other):
        if isinstance(other, Tick):
            return self.tick_number == other.tick_number
        return False
        

priority_type = Annotated[int, Field(ge=0, le=2)] # from 0 to 2, where 0 is low, 1 is medium, 2 is high
spread_type = Annotated[str, StringConstraints(pattern=r"^(evenly|asap)$")]
relation_type = Annotated[str, StringConstraints(pattern=r"^(before|after|around)$")] | None


class UserPrompt(BaseModel):
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
    relation_to_day_period: relation_type = None # before/after/around
    
    another_task_mentioned: Optional[str] = None # name of another task mentioned
    number_of_another_task_mentioned: Optional[int] = None
    relation_to_another_task_mentioned: relation_type = None # before/after/around
    
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
    
 
    def get_sleep_period_ticks(self, scope_start: datetime, scope_end: datetime) -> List[int]:
        """
        Get sleep period ticks for a given scope.
        This method should be used instead of the computed field property.
        """
        return Tick.time_window_to_list_of_ticks(
            self.sleep_period_start,
            self.sleep_period_end,
            scope_start,
            scope_end
        )
        
    
    def get_do_not_disturb_ticks(self, scope_start: datetime, scope_end: datetime) -> List[int]:
        """Get do not disturb period ticks for a given scope."""
        if self.do_not_disturb_start is None or self.do_not_disturb_end is None:
            return []
        return Tick.time_window_to_list_of_ticks(
            self.do_not_disturb_start,
            self.do_not_disturb_end,
            scope_start,
            scope_end
        )
    
 
    def get_preferred_hours_ticks(self, scope_start: datetime, scope_end: datetime) -> List[int]:
        """Get preferred hours ticks for a given scope."""
        return Tick.time_window_to_list_of_ticks(
            self.preferred_hours_start,
            self.preferred_hours_end,
            scope_start,
            scope_end
        )
    
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
    
with open("infra/test_data/llm.json", encoding="utf-8") as f:
    llm_raw = json.load(f)
llm_data = UserPrompt.model_validate(llm_raw)

with open("infra/test_data/ump.json", encoding="utf-8") as f:
    ump_raw = json.load(f)
ump_data = Ump.model_validate(ump_raw)
