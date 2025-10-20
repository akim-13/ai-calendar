from llm_ump_api import Tick, Ump, llm_data, ump_data
from database_api import events
from ortools.sat.python import cp_model
from collections import defaultdict

model = cp_model.CpModel()

# ==================== Scope Definition ====================
scope_start = llm_data.scope_start_tick
scope_end = llm_data.scope_end_tick
scope_length = scope_end - scope_start

# ==================== Task Parameters ====================
task_length = llm_data.task_length_ticks
# max_ticks_per_day = llm_data.max_allowed_ticks_per_day
break_between_sessions = ump_data.min_break_ticks
max_session_length = ump_data.max_session_ticks

# ==================== Reference Times ====================
reference_start = llm_data.scope_start_rounded
reference_end = llm_data.scope_end_rounded

# ==================== Extra functions for sets ====================
# Function to add 15 minutes break around unavailable ticks
def dilate_ticks(ticks, break_between_sessions):
    expanded = set()
    for tick in ticks:
        start = max(scope_start, tick - break_between_sessions)
        end = min(scope_end -1, tick + break_between_sessions)
        for t in range(start, end+1):
            expanded.add(t)
    return expanded

# ==================== Get Constraint Ticks ====================
sleep_ticks = set(ump_data.get_sleep_period_ticks(reference_start, reference_end))
dnd_ticks = set(ump_data.get_do_not_disturb_ticks(reference_start, reference_end))
busy_ticks = set(events.get_all_busy_ticks(reference_start))
busy_ticks_with_breaks = dilate_ticks(busy_ticks, break_between_sessions)

# Combine all hard constraints (For now there is no overlap handling)
hard_unavailable_ticks = sleep_ticks | dnd_ticks | busy_ticks

# Soft preferences 
preferred_ticks = set(ump_data.get_preferred_hours_ticks(reference_start, reference_end))

# Task-specific time window preferences (if applicable)
if llm_data.day_period_start and llm_data.day_period_end:
    task_period_ticks = set(llm_data.get_day_period_ticks)
else:
    task_period_ticks = set(range(scope_start, scope_end))  # All ticks allowed

# ==================== Prefiltering ====================
candidate_ticks = {tick for tick in task_period_ticks if scope_start <= tick < scope_end and tick not in hard_unavailable_ticks}

if len(candidate_ticks) < task_length:
    raise ValueError(f"Not enough available ticks to schedule. Only {len(candidate_ticks)} available.")

tick_vars = {tick: model.NewBoolVar(f"tick_{tick}") for tick in sorted(candidate_ticks)}

# ==================== Hard Constraints ====================

# 1. Must schedule exactly task_length ticks
model.add(sum(tick_vars.values()) == task_length)

# 2. Evenly distributed constraint

# 3. Max ticks per day constraint
ticks_in_day = 24 * 60 // Tick.MINUTES_PER_TICK

def day_index(tick):
    return (tick // ticks_in_day)

by_day_ticks = defaultdict(list)
for ticks, var in tick_vars.items():
    by_day_ticks[day_index(ticks)].append(var)
    
for day, vars_in_day in by_day_ticks.items():
    model.add(sum(vars_in_day) <= max_session_length)