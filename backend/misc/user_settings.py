from enum import Enum

# A string-backed Enum allows for type safety,
# immutability, and other nice features.
class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"

