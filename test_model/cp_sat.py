from llm_ump_api import Tick, Ump, llm_data, ump_data
from database_api import events
from ortools.sat.python import cp_model

model = cp_model.CpModel()

# ==================== Scope Definition ====================
scope_start = llm_data.scope_start_tick
scope_end = llm_data.scope_end_tick
scope_length = scope_end - scope_start

# ==================== Task Parameters ====================
task_length = llm_data.task_length_ticks
max_ticks_per_day = llm_data.max_allowed_ticks_per_day

# ==================== Reference Times ====================
reference_start = llm_data.scope_start_rounded
reference_end = llm_data.scope_end_rounded

# ==================== Get Constraint Ticks ====================
# Hard constraints (absolutely cannot schedule here)
sleep_ticks = set(ump_data.get_sleep_period_ticks(reference_start, reference_end))
dnd_ticks = set(ump_data.get_do_not_disturb_ticks(reference_start, reference_end))
busy_ticks = set(events.get_all_busy_ticks(reference_start))

# Combine all hard constraints
hard_unavailable_ticks = sleep_ticks | dnd_ticks | busy_ticks

# Soft preferences (prefer to schedule here, but not required)
preferred_ticks = set(ump_data.get_preferred_hours_ticks(reference_start, reference_end))

# Task-specific time window preferences (if applicable)
if llm_data.day_period_start and llm_data.day_period_end:
    task_period_ticks = set(llm_data.get_day_period_ticks)
else:
    task_period_ticks = set(range(scope_start, scope_end))  # All ticks allowed

# ==================== Decision Variables ====================
# Create a boolean variable for each tick in the scope
tick_vars = {}
for tick in range(scope_start, scope_end):
    tick_vars[tick] = model.new_bool_var(f'tick_{tick}')

# ==================== Hard Constraints ====================

# 1. Cannot schedule during hard unavailable times
for tick in hard_unavailable_ticks:
    if scope_start <= tick < scope_end:
        model.add(tick_vars[tick] == 0)

# 2. Must schedule exactly task_length ticks
model.add(sum(tick_vars.values()) == task_length)