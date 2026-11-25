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


def consumption_view(by_date, now):
    """Select a verified API value without inventing hourly measurements."""
    date = max(by_date)
    latest = by_date[date]
    integrity = consumption_integrity(latest, by_date.get(date - timedelta(hours=1)))
    selected = None
    for candidate in sorted(by_date, reverse=True):
        row = by_date[candidate]
        if consumption_integrity(row, by_date.get(candidate - timedelta(hours=1))) == "consistent":
            selected = candidate
            break
    # A normal update can be delayed until the next hourly polling cycle.
    stale = now - date >= timedelta(hours=2)
    quality = ("stale" if stale else
               {"consistent": "confirmed", "pending": "pending",
                "unverifiable": "unverifiable"}[integrity])
    # Do not keep a value indefinitely or carry it across a meter replacement.
    if selected is not None:
        if (now - selected >= timedelta(hours=2)
                or by_date[selected].get("serial_number") != latest.get("serial_number")):
            selected = None
    return {
        "consumption": by_date[selected]["consumption"] if selected is not None else None,
        "consumption_time": selected,
        "data_quality": quality,
    }
