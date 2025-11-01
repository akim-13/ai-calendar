from pydantic import BaseModel, ConfigDict, computed_field
from typing import List
from decimal import Decimal
from datetime import datetime, time
from user_prompt import UserPrompt
from tick import Tick
import json


class UMP(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    allowed_weekdays: List[int]
    min_session_hours: Decimal = Decimal("0.5")
    max_session_hours: Decimal = Decimal("2.0")
    min_break_between_sessions_hours: Decimal = Decimal("0.5")
    
    sleep_period_start: time = time(23, 0)
    sleep_period_end:   time = time(7, 0)
    
    do_not_disturb_start: time | None = None
    do_not_disturb_end:  time | None = None
    
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
ump_data = UMP.model_validate(ump_raw)
