from enum import IntEnum, StrEnum


class Priority(IntEnum):
    """Task importance or urgency level."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class Spread(StrEnum):
    """How sessions are distributed within the available time window."""
    UNIFORM = "uniform"
    FRONTLOADED = "frontloaded"


class Relation(StrEnum):
    """Temporal relation to another reference (period or task)."""
    BEFORE = "before"
    AFTER = "after"
    AROUND = "around"


class RecurrenceFrequency(StrEnum):
    """How often a recurring task repeats."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"


class Weekday(IntEnum):
    """Days of the week, Monday=0 .. Sunday=6."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
