from enum import Enum


class Priority(int, Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class Spread(str, Enum):
    UNIFORM = "uniform"
    FRONTLOADED = "frontloaded"

class Relation(str, Enum):
    BEFORE = "before"
    AFTER = "after"
    AROUND = "around"

class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"
