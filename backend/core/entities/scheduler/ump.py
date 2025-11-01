from pydantic import BaseModel, ConfigDict, computed_field
from typing import List
from decimal import Decimal
from datetime import datetime, time
from core.entities.scheduler.tick import Tick
from core.entities.scheduler.windows import TimeWindow
from core.values.enums import Weekday


class Ump(BaseModel):
    """User Model Parameters controlling scheduling behaviour."""
    model_config = ConfigDict(extra="forbid")

    allowed_weekdays: List[Weekday]
    min_session_hours: Decimal = Decimal("0.5")
    max_session_hours: Decimal = Decimal("2.0")
    min_break_between_sessions_hours: Decimal = Decimal("0.5")

    sleep_window: TimeWindow = TimeWindow(start=time(23, 0), end=time(7, 0))
    do_not_disturb_window: TimeWindow | None = None
    preferred_window: TimeWindow = TimeWindow(start=time(12, 0), end=time(20, 0))

    # --- Conversion methods --------------------------------------------------

    def get_sleep_ticks(self, scope_start: datetime, scope_end: datetime) -> List[int]:
        """Return tick numbers for the user's sleep window within the given scope."""
        return Tick.time_window_to_list_of_ticks(
            self.sleep_window.start,
            self.sleep_window.end,
            scope_start,
            scope_end,
        )

    def get_do_not_disturb_ticks(self, scope_start: datetime, scope_end: datetime) -> List[int]:
        """Return tick numbers for the user's DND window within the given scope."""
        if self.do_not_disturb_window is None:
            return []
        return Tick.time_window_to_list_of_ticks(
            self.do_not_disturb_window.start,
            self.do_not_disturb_window.end,
            scope_start,
            scope_end,
        )

    def get_preferred_ticks(self, scope_start: datetime, scope_end: datetime) -> List[int]:
        """Return tick numbers for the user's preferred working hours within the given scope."""
        return Tick.time_window_to_list_of_ticks(
            self.preferred_window.start,
            self.preferred_window.end,
            scope_start,
            scope_end,
        )

    # --- Computed fields -----------------------------------------------------

    @computed_field
    @property
    def min_session_ticks(self) -> int:
        """Convert minimum session hours to ticks."""
        return Tick.from_hours(float(self.min_session_hours))

    @computed_field
    @property
    def max_session_ticks(self) -> int:
        """Convert maximum session hours to ticks."""
        return Tick.from_hours(float(self.max_session_hours))

    @computed_field
    @property
    def min_break_ticks(self) -> int:
        """Convert minimum break hours between sessions to ticks."""
        return Tick.from_hours(float(self.min_break_between_sessions_hours))
