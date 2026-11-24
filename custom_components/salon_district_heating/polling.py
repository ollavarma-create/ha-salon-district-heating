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

def consumption_integrity(latest, previous):
    """Return consistent, pending or unverifiable (provisional interval semantics)."""
    from math import isfinite
    def valid(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value) and value >= 0
    consumption = latest.get("consumption")
    if not valid(consumption):
        return "pending"
    if previous is None or not latest.get("serial_number") or latest.get("serial_number") != previous.get("serial_number"):
        return "unverifiable"
    a, b = latest.get("reading_total"), previous.get("reading_total")
    if not valid(a) or not valid(b) or a < b:
        return "unverifiable"
    return "consistent" if abs((a - b) - consumption) < 0.001 else "pending"
