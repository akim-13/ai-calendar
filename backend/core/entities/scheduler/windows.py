from datetime import time, datetime
from pydantic import BaseModel


class TimeWindow(BaseModel):
    """Represents a recurring daily time window."""
    start: time
    end: time

    def is_full_day(self) -> bool:
        return self.start == self.end

    def spans_midnight(self) -> bool:
        """True if the window crosses midnight."""
        return self.end < self.start


class DateTimeWindow(BaseModel):
    """Represents a single continuous datetime range (non-recurring)."""

    start: datetime
    end: datetime

    def duration(self) -> float:
        """Duration in hours."""
        return (self.end - self.start).total_seconds() / 3600
