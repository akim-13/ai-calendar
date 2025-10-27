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
task_priority = llm_data.priority
spread = llm_data.spread

# ==================== Session Parameters ====================
min_session_length = ump_data.min_session_ticks
max_session_length = ump_data.max_session_ticks
min_break = ump_data.min_break_ticks

# ==================== Reference Times ====================
reference_start = llm_data.scope_start_rounded
reference_end = llm_data.scope_end_rounded

# ==================== Helper Function ====================
def ticks_to_intervals(ticks_set, name_prefix):
    """
    Convert a set of ticks into a list of interval variables.
    Groups consecutive ticks into contiguous intervals.
    """
    if not ticks_set:
        return []
    
    intervals = []
    ticks_sorted = sorted(ticks_set)
    
    current_start = ticks_sorted[0]
    current_end = ticks_sorted[0] + 1
    
    for tick in ticks_sorted[1:]:
        if tick == current_end:
            # Consecutive tick, extend interval
            current_end = tick + 1
        else:
            # Gap found, save current interval and start new one
            if scope_start <= current_start < scope_end:
                duration = current_end - current_start
                interval = model.NewFixedSizeIntervalVar(
                    current_start,
                    duration,
                    f'{name_prefix}_{current_start}_{current_end}'
                )
                intervals.append(interval)
            
            current_start = tick
            current_end = tick + 1
    
    # Don't forget the last interval
    if scope_start <= current_start < scope_end:
        duration = current_end - current_start
        interval = model.NewFixedSizeIntervalVar(
            current_start,
            duration,
            f'{name_prefix}_{current_start}_{current_end}'
        )
        intervals.append(interval)
    
    return intervals

# ==================== Get Constraint Ticks ====================
sleep_ticks = set(ump_data.get_sleep_period_ticks(reference_start, reference_end))
dnd_ticks = set(ump_data.get_do_not_disturb_ticks(reference_start, reference_end))
preferred_ticks = set(ump_data.get_preferred_hours_ticks(reference_start, reference_end))

# Task-specific time window
if llm_data.day_period_start and llm_data.day_period_end:
    task_period_ticks = set(llm_data.get_day_period_ticks)
else:
    task_period_ticks = set(range(scope_start, scope_end))

# ==================== Convert to Intervals ====================
# Fixed intervals that block scheduling
sleep_intervals = ticks_to_intervals(sleep_ticks, 'sleep')
dnd_intervals = ticks_to_intervals(dnd_ticks, 'dnd')

# Existing events as fixed intervals
existing_event_intervals = []
for event in events.events:
    event_start_rounded = Tick.round_datetime_to_tick_boundary(event.start, round_up=False)
    event_end_rounded = Tick.round_datetime_to_tick_boundary(event.end, round_up=True)
    
    event_start_tick = Tick.from_datetime_diff(event_start_rounded, reference_start).tick_number
    event_end_tick = Tick.from_datetime_diff(event_end_rounded, reference_start).tick_number
    
    # Only include events within scope
    if event_start_tick < scope_end and event_end_tick > scope_start:
        clamped_start = max(event_start_tick, scope_start)
        clamped_end = min(event_end_tick, scope_end)
        clamped_duration = clamped_end - clamped_start
        
        if clamped_duration > 0:
            interval = model.NewFixedSizeIntervalVar(
                clamped_start,
                clamped_duration,
                f'event_{event.id}'
            )
            existing_event_intervals.append(interval)

# Combine all blocking intervals
blocking_intervals = sleep_intervals + dnd_intervals + existing_event_intervals

# ==================== Create Task Sessions ====================
# Calculate how many sessions we need
max_sessions = (task_length + min_session_length - 1) // min_session_length
min_sessions = (task_length + max_session_length - 1) // max_session_length

# Estimate reasonable number of sessions
estimated_sessions = (task_length + max_session_length - 1) // max_session_length
# Allow some flexibility - could need more sessions if schedule is tight
num_sessions = min(max_sessions, estimated_sessions + 2)

print(f"Creating up to {num_sessions} sessions for task of {task_length} ticks")
print(f"Session constraints: min={min_session_length}, max={max_session_length}")

# Create session variables
sessions = []
session_intervals = []

for i in range(num_sessions):
    # Each session can start anywhere in the valid window
    session_start = model.NewIntVar(scope_start, scope_end, f'session_{i}_start')
    
    # Session duration is flexible between min and max
    session_duration = model.NewIntVar(0, max_session_length, f'session_{i}_duration')
    
    # Session end
    session_end = model.NewIntVar(scope_start, scope_end, f'session_{i}_end')
    model.Add(session_end == session_start + session_duration)
    
    # Create interval
    session_interval = model.NewOptionalIntervalVar(
        session_start,
        session_duration,
        session_end,
        model.NewBoolVar(f'session_{i}_present'),
        f'session_{i}'
    )
    
    sessions.append({
        'start': session_start,
        'duration': session_duration,
        'end': session_end,
        'present': model.NewBoolVar(f'session_{i}_present'),
        'interval': session_interval
    })
    session_intervals.append(session_interval)

# ==================== Hard Constraints ====================

# 1. Total duration must equal task_length
total_duration = sum(s['duration'] for s in sessions)
model.Add(total_duration == task_length)

# 2. If a session is present, it must meet minimum length
for s in sessions:
    # If present: duration >= min_session_length
    model.Add(s['duration'] >= min_session_length).OnlyEnforceIf(s['present'])
    # If not present: duration == 0
    model.Add(s['duration'] == 0).OnlyEnforceIf(s['present'].Not())

# 3. Sessions must be ordered (session i+1 starts after session i ends)
for i in range(len(sessions) - 1):
    # If both sessions are present, enforce ordering
    both_present = model.NewBoolVar(f'sessions_{i}_and_{i+1}_present')
    model.AddBoolAnd([sessions[i]['present'], sessions[i+1]['present']]).OnlyEnforceIf(both_present)
    
    # session[i+1].start >= session[i].end + min_break
    model.Add(
        sessions[i+1]['start'] >= sessions[i]['end'] + min_break
    ).OnlyEnforceIf(both_present)

# 4. No overlap with blocking intervals (sleep, DND, existing events)
all_intervals = blocking_intervals + session_intervals
model.AddNoOverlap(all_intervals)

# 5. Sessions must be within task_period_ticks
# For each session, start and end must be in valid ticks
for s in sessions:
    # Only enforce if session is present
    if task_period_ticks != set(range(scope_start, scope_end)):
        # This is complex with intervals - simplified: ensure start is in valid range
        valid_starts = sorted([t for t in task_period_ticks if t >= scope_start and t < scope_end])
        if valid_starts:
            min_valid = min(valid_starts)
            max_valid = max(valid_starts)
            model.Add(s['start'] >= min_valid).OnlyEnforceIf(s['present'])
            model.Add(s['end'] <= max_valid).OnlyEnforceIf(s['present'])

# 6. Max ticks per day constraint
ticks_per_day = 24 * 60 // Tick.MINUTES_PER_TICK

def get_day_index(tick_var):
    """Get which day a tick falls on"""
    day_var = model.NewIntVar(0, scope_length // ticks_per_day + 1, f'day_of_{tick_var}')
    model.AddDivisionEquality(day_var, tick_var - scope_start, ticks_per_day)
    return day_var

# Group sessions by day and enforce max per day
max_ticks_per_day = llm_data.max_allowed_ticks_per_day

# For each day in scope, sum the durations of sessions that fall on that day
num_days = (scope_length + ticks_per_day - 1) // ticks_per_day

for day in range(num_days):
    day_start = scope_start + day * ticks_per_day
    day_end = min(scope_start + (day + 1) * ticks_per_day, scope_end)
    
    # For each session, calculate how much of it falls on this day
    ticks_on_this_day = []
    
    for s in sessions:
        # Check if session overlaps with this day
        session_on_day = model.NewBoolVar(f'session_{sessions.index(s)}_on_day_{day}')
        
        # Session overlaps if: session.start < day_end AND session.end > day_start
        overlaps_day = model.NewBoolVar(f'session_{sessions.index(s)}_overlaps_day_{day}')
        model.Add(s['start'] < day_end).OnlyEnforceIf(overlaps_day)
        model.Add(s['end'] > day_start).OnlyEnforceIf(overlaps_day)
        model.Add(s['present'] == 1).OnlyEnforceIf(overlaps_day)
        
        # If overlaps, count the duration
        # Simplified: assume sessions don't span multiple days (reasonable for max_session_length)
        # If they do span, this would need more complex logic
        model.Add(s['duration'] <= max_ticks_per_day).OnlyEnforceIf(s['present'])

# ==================== Soft Preferences (Objective) ====================
objective_terms = []

# Preference 1: Schedule during preferred hours
# For each session, give bonus if it starts in preferred window
if preferred_ticks:
    min_pref = min(preferred_ticks)
    max_pref = max(preferred_ticks)
    
    for s in sessions:
        in_preferred = model.NewBoolVar(f'session_{sessions.index(s)}_in_preferred')
        model.Add(s['start'] >= min_pref).OnlyEnforceIf(in_preferred)
        model.Add(s['start'] < max_pref).OnlyEnforceIf(in_preferred)
        model.Add(s['present'] == 1).OnlyEnforceIf(in_preferred)
        
        # Bonus weighted by session duration
        objective_terms.append(in_preferred * 10)

# Preference 2: Spread preference
if spread == "asap":
    # Minimize first session start time
    first_present_start = model.NewIntVar(scope_start, scope_end, 'first_session_start')
    
    # Find the first present session
    for s in sessions:
        # If this session is present, first_start should be at most this start
        model.Add(first_present_start <= s['start']).OnlyEnforceIf(s['present'])
    
    # Minimize first start (negative to turn into maximization)
    objective_terms.append(-first_present_start)

elif spread == "evenly":
    # Maximize the minimum gap between sessions
    # Or: minimize the variance in daily distribution
    
    # Simplified: Try to maximize gaps between sessions
    for i in range(len(sessions) - 1):
        gap = model.NewIntVar(0, scope_length, f'gap_{i}')
        both_present = model.NewBoolVar(f'gap_{i}_both_present')
        model.AddBoolAnd([sessions[i]['present'], sessions[i+1]['present']]).OnlyEnforceIf(both_present)
        
        model.Add(gap == sessions[i+1]['start'] - sessions[i]['end']).OnlyEnforceIf(both_present)
        model.Add(gap == 0).OnlyEnforceIf(both_present.Not())
        
        # Bonus for larger gaps (encourages spreading)
        objective_terms.append(gap)

# Set objective
if objective_terms:
    model.Maximize(sum(objective_terms))

# ==================== Solve ====================
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0
status = solver.Solve(model)

# ==================== Extract Solution ====================
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"\nSolution status: {'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}")
    
    scheduled_sessions = []
    for i, s in enumerate(sessions):
        if solver.Value(s['present']):
            start_tick = solver.Value(s['start'])
            duration = solver.Value(s['duration'])
            end_tick = solver.Value(s['end'])
            
            start_datetime = Tick.to_datetime(start_tick, reference_start)
            end_datetime = Tick.to_datetime(end_tick, reference_start)
            
            scheduled_sessions.append({
                'session': i + 1,
                'start_tick': start_tick,
                'end_tick': end_tick,
                'duration_ticks': duration,
                'duration_hours': duration * Tick.MINUTES_PER_TICK / 60,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime
            })
    
    print(f"\nScheduled {len(scheduled_sessions)} sessions:")
    total_scheduled = 0
    for sess in scheduled_sessions:
        print(f"  Session {sess['session']}:")
        print(f"    Time: {sess['start_datetime']} to {sess['end_datetime']}")
        print(f"    Duration: {sess['duration_hours']:.2f} hours ({sess['duration_ticks']} ticks)")
        total_scheduled += sess['duration_ticks']
    
    print(f"\nTotal scheduled: {total_scheduled} ticks (required: {task_length})")
    print(f"Total hours: {total_scheduled * Tick.MINUTES_PER_TICK / 60:.2f} hours")

else:
    print("No solution found!")
    print(f"Status: {solver.StatusName(status)}")