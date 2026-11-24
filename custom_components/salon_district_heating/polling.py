"""UTC-aligned polling policy, independent of Home Assistant."""
from datetime import timedelta
from random import randint

def next_poll(now, complete):
    hour = now.replace(minute=0, second=0, microsecond=0)
    minutes = (20,) if complete else (20, 30, 40, 50)
    for minute in minutes:
        target = hour + timedelta(minutes=minute)
        if target > now:
            return target + timedelta(seconds=randint(0, 30))
    return hour + timedelta(hours=1, minutes=20, seconds=randint(0, 30))

def current_sample(now, stamp):
    # Provisional assumption: date labels the latest expected hourly record.
    return stamp >= now.replace(minute=0, second=0, microsecond=0)
