import json

with open("d:/ai-calendar/test_model/timetable.json", "r", encoding = "utf-8") as f:
    timetable = json.load(f)
    
extra_days = 30
ticks_per_day = timetable['per_day_ticks']

timetable['week']['ticks'].extend([""] * (extra_days * ticks_per_day))

timetable['week']['legend'].append("Extra 30 free days")

with open("d:/ai-calendar/test_model/extended_timetable.json", "w", encoding = "utf-8") as f:
    json.dump(timetable, f, indent = 2)
    
