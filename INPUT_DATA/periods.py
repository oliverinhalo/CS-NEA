import json
from datetime import datetime

normal_day_times = [
    ("08:30", "09:15"),
    ("09:20", "10:05"),
    ("10:10", "10:55"),
    ("11:30", "12:15"),
    ("12:20", "13:05"),
    ("14:45", "15:30"),
    ("15:35", "16:20"),
]

wednesday_times = [
    ("08:30", "09:15"),
    ("09:20", "10:05"),
    ("10:10", "10:55"),
    ("11:30", "12:15"),
    ("12:20", "13:05"),
    ("14:10", "14:55"),
    ("15:00", "15:45"),
]

days = [0,1,2,3,4,5]
weeks = [1, 2]

periods = {}
period_id = 1

for week in weeks:
    for day in days:
        if day == 2:
            schedule = wednesday_times
        else:
            schedule = normal_day_times

        for start_str, end_str in schedule:
            periods[f"{period_id}"] = {
                "start": start_str,
                "end": end_str,
                "day": day,
                "week": week
            }
            period_id += 1

output_path = "INPUT_DATA/periods.json"
with open(output_path, "w") as f:
    json.dump(periods, f, indent=2)