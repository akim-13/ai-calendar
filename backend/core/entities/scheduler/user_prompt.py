from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from typing import List
from datetime import datetime
from core.entities.scheduler.tick import Tick
from core.entities.scheduler.windows import TimeWindow, DateTimeWindow
from core.values.enums import Priority, Spread, Relation


class UserPrompt(BaseModel):
    """Model representing structured task information parsed from the LLM."""
    # Forbid unknown fields from LLM output
    model_config = ConfigDict(extra="forbid")  

    title: str
    tag: str
    task_length_hours: int

    # Overall scheduling scope (absolute datetimes)
    scope: DateTimeWindow

    priority: Priority
    max_allowed_hours_per_day: int = 2  # Max hours per day to spend on this task
    spread: Spread = Spread.UNIFORM

    # Optional daily time preference (e.g. "between 09:00 and 17:00")
    day_period: TimeWindow | None = None
    relation_to_day_period: Relation | None = None

    # Optional relation to another mentioned task
    another_task_mentioned: str | None = None
    number_of_another_task_mentioned: int | None = None
    relation_to_another_task_mentioned: Relation | None = None

    @field_validator(
        'relation_to_day_period',
        'another_task_mentioned',
        'relation_to_another_task_mentioned',
        mode='before'
    )
    @classmethod
    def empty_str_to_none(cls, value):
        """Convert empty strings to None for optional fields."""
        if value == '':
            return None
        return value

    # --- Computed fields -----------------------------------------------------

    @computed_field
    @property
    def scope_start_rounded(self) -> datetime:
        """Scope start rounded down to 5-minute boundary."""
        return Tick.round_datetime_to_tick_boundary(self.scope.start, round_up=False)

    @computed_field
    @property
    def scope_end_rounded(self) -> datetime:
        """Scope end rounded up to 5-minute boundary."""
        return Tick.round_datetime_to_tick_boundary(self.scope.end, round_up=True)

    @computed_field
    @property
    def task_length_ticks(self) -> int:
        """Convert task length from hours to ticks."""
        return Tick.from_hours(self.task_length_hours)

    @computed_field
    @property
    def scope_start_tick(self) -> int:
        """Scope start is always tick 0 (after rounding)."""
        return 0

    @computed_field
    @property
    def scope_end_tick(self) -> int:
        """Convert scope.end datetime to tick (relative to rounded scope.start = 0)."""
        return int(Tick.from_datetime_diff(self.scope_end_rounded, self.scope_start_rounded))

    @computed_field
    @property
    def max_allowed_ticks_per_day(self) -> int:
        """Convert max hours per day to ticks."""
        return Tick.from_hours(self.max_allowed_hours_per_day)

    @computed_field
    @property
    def scope_duration_ticks(self) -> int:
        """Calculate total ticks in the scope."""
        return int(self.scope_end_tick) - int(self.scope_start_tick)

    @computed_field
    @property
    def day_period_ticks(self) -> List[int]:
        """Get tick numbers corresponding to the daily period across the scope."""
        if self.day_period is None:
            return []
        return Tick.time_window_to_list_of_ticks(
            self.day_period.start,
            self.day_period.end,
            self.scope_start_rounded,
            self.scope_end_rounded,
        )
