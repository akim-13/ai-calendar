"""math coursework by the end of the week, 10 hours, evenly spread, after afternoon"""

import json
from ortools.sat.python import cp_model
from typing import List, Tuple, Dict, Any
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
        
        # Task parameters
        self.task_ticks = self.llm_data["task_ticks_length"]

    def create_time_windows(self):
        """Create time window masks for different periods."""
        self.windows = {}
        
        periods = {
            'morning': (0, 48),      # 00:00 - 12:00
            'afternoon': (48, 72),   # 12:00 - 18:00  
            'evening': (72, 96),     # 18:00 - 24:00
        }
        
        for period, (start_tick, end_tick) in periods.items():
            self.windows[period] = []
            for day in range(7):
                day_start = day * self.ticks_per_day
                self.windows[period].extend(range(day_start + start_tick, day_start + end_tick))
                """The result is a dictinoary of arrays with all preiods for each day a week"""
                
    def get_valid_days_from_deadline(self, task_deadline: str) -> List[int]:
        """String of valid day indices (0=Mon, 6=Sun)."""
        if not task_deadline:
            return list(range(7))   # All days valid if no deadline
        
        deadline_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        deadline_day = deadline_map.get(task_deadline.lower())
        if deadline_day is None:
            return list(range(7))   # Invalid deadline, allow all days
                                    # !!! Here we will need to send messages to user (later)
        
        # Return all days up to including the deadline
        return list(range(deadline_day + 1))

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
                    around_buffer = 8  # 2 hours in 15-min ticks
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
                
        print (sorted(list(valid_ticks)))
        
if __name__ == "__main__":
    scheduler = TaskScheduler("timetable.json", "llm.json")
    scheduler.get_day_period_constraints()
    
        