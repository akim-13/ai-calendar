from typing import List
from datetime import datetime, time, timedelta


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
