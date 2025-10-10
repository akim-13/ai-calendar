"""math coursework by the end of the week, 10 hours, evenly spread, after afternoon"""

import json
from ortools.sat.python import cp_model
from typing import List, Tuple, Dict, Any, Optional
import datetime
import math

class TaskScheduler:
    def __init__(self, timetable_file: str, llm_file: str):
        """Initialize scheduler with timetable and LLM files."""
        self.load_data(timetable_file, llm_file)
        self.compute_derived_values()
        self.create_time_windows()
        
    def load_data(self, timetable_file: str, llm_file: str):
        """Load JSON data files."""
        with open(timetable_file) as f:
            self.timetable_data = json.load(f)
            
        with open(llm_file) as f:
            self.llm_data = json.load(f)
    
    # In the future take the variable from the database
    def compute_derived_values(self):
        """Compute constants and masks from timetable data."""
        self.tick_min = self.timetable_data["tick_min"]
        self.ticks = self.timetable_data["week"]["ticks"]
        self.T = len(self.ticks)
        self.ticks_per_day = 24 * (60 // self.tick_min)
        
        # Busy mask: 1 if busy, 0 if free
        self.busy = [1 if tick != "" else 0 for tick in self.ticks]
        
        # Day mapping
        self.day_of_t = [t // self.ticks_per_day for t in range(self.T)]
        
        # Number of days present
        self.num_days = math.ceil(self.T / self.ticks_per_day)

        # Task parameters
        self.task_ticks = self.llm_data["task_ticks_length"]

        self.today: datetime.date = datetime.date.today()
        self.absolute_deadline: Optional[datetime.date] = None
        
        iso_deadline = self.llm_data.get("absolute_deadline_datetime", "")
        if iso_deadline:
            try:
                # Parse as datetime first, then extract date
                deadline_datetime = datetime.datetime.fromisoformat(iso_deadline)
                self.absolute_deadline = deadline_datetime.date()
            except ValueError:
                print(f"Invalid ISO datetime format: {iso_deadline}")
                self.absolute_deadline = None
                
        
    def create_time_windows(self):
        """Create time window masks for different periods."""
        self.windows = {}
        
        periods = {
            'night': (0, 24),         # 00:00 - 6:00
            'morning': (24, 48),     # 06:00 - 12:00
            'afternoon': (48, 72),   # 12:00 - 18:00  
            'evening': (72, 96),     # 18:00 - 24:00
        }
        
        for period, (start_tick, end_tick) in periods.items():
            self.windows[period] = []
            
            for day in range(self.num_days):
                day_start = day * self.ticks_per_day
                # Guard against not full ticks per day
                period_start = min(day_start + start_tick, self.T)
                period_end = min(day_start + end_tick, self.T)
                if period_start < period_end:
                    self.windows[period].extend(range(period_start, period_end))
                """The result is a dictinoary of arrays with all preiods for each day a week"""
                
    def get_valid_days_from_deadline(self, task_deadline: str) -> List[int]:
        """Return valid day indices based on task deadline."""
        
        if self.absolute_deadline:
            days_until_deadline = (self.absolute_deadline - self.today).days
            if days_until_deadline < 0:
                return []  # Deadline passed
            max_day = min(days_until_deadline, self.num_days - 1)
            return list(range(max_day + 1))
        return list(range(self.num_days))
        

    def get_day_period_constraints(self) -> List[int]:
        """Get valid ticks based on day period constraints and deadline."""
        day_period_start = self.llm_data.get("day_period_start", "")
        day_period_end = self.llm_data.get("day_period_end", "")
        relation = self.llm_data.get("relation_to_day_period", "")
        task_deadline = self.llm_data.get("task_deadline", "")
        
        # Get deadline constraint (which days are valid)
        valid_days = self.get_valid_days_from_deadline(task_deadline)
        
        # If no day period constraints, return all ticks within deadline days
        if not day_period_start and not relation:
            valid_ticks = set()
            for day in valid_days:
                day_start = day * self.ticks_per_day
                day_end = min(day_start + self.ticks_per_day, self.T)
                valid_ticks.update(range(day_start, day_end))
            return sorted(list(valid_ticks))
            
        valid_ticks = set()
        
        if day_period_start != "" and day_period_end == "":
            # Single boundary
            boundary = int(day_period_start)
            
            for day in valid_days:
                day_start = day * self.ticks_per_day
                day_end = min(day_start + self.ticks_per_day, self.T) # In case timetable data is smaller than 7 days
                
                if relation == "before":
                    # Schedule strictly before the boundary
                    valid_ticks.update(range(day_start, min(day_start + boundary, day_end)))
                elif relation == "after":
                    # Schedule at/after the boundary
                    valid_ticks.update(range(day_start + boundary, day_end))
                elif relation == "around":
                    # Schedule within ±2 hours of boundary (8 ticks = 2 hours for 15-min ticks)
                    self.around_buffer_hours = self.llm_data.get("around_buffer_hours", 2)
                    around_buffer = self.around_buffer_hours * (60 // self.tick_min)
                    around_start = max(day_start, day_start + boundary - around_buffer)
                    around_end = min(day_end, day_start + boundary + around_buffer)
                    valid_ticks.update(range(around_start, around_end))
                    
        elif day_period_start != "" and day_period_end != "":
            # Window constraint
            start_tick = int(day_period_start)
            end_tick = int(day_period_end)
            
            for day in valid_days:
                day_start = day * self.ticks_per_day
                day_end = min(day_start + self.ticks_per_day, self.T)
                
                if relation == "before":
                    # Schedule before the window starts
                    valid_ticks.update(range(day_start, min(day_start + start_tick, day_end)))
                elif relation == "after":
                    # Schedule after the window ends
                    valid_ticks.update(range(max(day_start + end_tick, day_start), day_end))
                elif relation == "around":
                    # Schedule within ±2 hours of the window
                    around_buffer = 8  # 2 hours in 15-min ticks
                    around_start = max(day_start, day_start + start_tick - around_buffer)
                    around_end = min(day_end, day_start + end_tick + around_buffer)
                    valid_ticks.update(range(around_start, around_end))
                else:
                    # No relation specified, allow within window
                    valid_ticks.update(range(day_start + start_tick, min(day_start + end_tick, day_end)))
        else:
            # Only deadline constraint applies
            for day in valid_days:
                day_start = day * self.ticks_per_day
                day_end = min(day_start + self.ticks_per_day, self.T)
                valid_ticks.update(range(day_start, day_end))
                
        result = sorted(list(valid_ticks))
        print(result)
        return result
        
if __name__ == "__main__":
    try:
        scheduler = TaskScheduler("test_model\\extended_timetable.json", "test_model\\llm.json")
        
        print(f"Debug Info:")
        print(f"  - Total ticks: {scheduler.T}")
        print(f"  - Ticks per day: {scheduler.ticks_per_day}")
        print(f"  - Number of days: {scheduler.num_days}")
        print(f"  - Task ticks needed: {scheduler.task_ticks}")
        print(f"  - Today: {scheduler.today}")
        print(f"  - Absolute deadline: {scheduler.absolute_deadline}")
        
        # Count free/busy ticks
        print(f"  - Free ticks: {scheduler.busy.count(0)}")
        print(f"  - Busy ticks: {scheduler.busy.count(1)}")
        
        # Check valid days
        valid_days = scheduler.get_valid_days_from_deadline("")
        print(f"  - Valid days for scheduling: {valid_days}")
        
        # Get constraints
        print(f"\nGetting day period constraints...")
        valid_ticks = scheduler.get_day_period_constraints()
        print(f"✓ Valid ticks found: {len(valid_ticks)}")
        
        if valid_ticks:
            print(f"  First 10 valid ticks: {valid_ticks[:10]}")
            print(f"  Last 10 valid ticks: {valid_ticks[-10:]}")
        else:
            print(" No valid ticks found!")
            
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        