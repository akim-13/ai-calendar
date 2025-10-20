from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import List, Set
from datetime import datetime
from llm_ump_api  import Tick
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
    
    def to_tick_range(self, reference_datetime: datetime) -> List[int]:
        """
        Convert this event to a list of tick numbers.
        
        Args:
            reference_datetime: The reference datetime (typically scope_start_rounded)
            
        Returns:
            List of tick numbers that this event occupies
        """
        # Round event times to tick boundaries
        start_rounded = Tick.round_datetime_to_tick_boundary(self.start, round_up=False)
        end_rounded = Tick.round_datetime_to_tick_boundary(self.end, round_up=True)
        
        # Convert to tick numbers
        start_tick = Tick.from_datetime_diff(start_rounded, reference_datetime).tick_number
        end_tick = Tick.from_datetime_diff(end_rounded, reference_datetime).tick_number
        
        # Return range of ticks (end_tick is exclusive)
        return list(range(start_tick, end_tick))


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
    
    
    def get_all_busy_ticks(self, reference_datetime: datetime) -> List[int]:
        busy_ticks: Set[int] = set()
        
        for event in self.events:
            event_ticks = event.to_tick_range(reference_datetime)
            busy_ticks.update(event_ticks)
        
        return sorted(list(busy_ticks))
    
    
    def get_busy_ticks_by_tag(self, reference_datetime: datetime, tag: str) -> List[int]:
        """
        Get busy ticks from events with a specific tag.
        
        Args:
            reference_datetime: The reference datetime
            tag: Tag to filter by
            
        Returns:
            Sorted list of unique tick numbers occupied by events with the given tag
        """
        busy_ticks: Set[int] = set()
        
        for event in self.events:
            if event.tag == tag:
                event_ticks = event.to_tick_range(reference_datetime)
                busy_ticks.update(event_ticks)
        
        return sorted(list(busy_ticks))


with open("test_model/database.json", encoding="utf-8") as f:
    database_raw = json.load(f)
    
events = EventList(events=database_raw)