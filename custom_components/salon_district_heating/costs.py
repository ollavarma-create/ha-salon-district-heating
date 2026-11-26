"""Persistent, timestamp-keyed estimates; no billing or historical import."""
from datetime import datetime, timedelta
from calendar import monthrange
from decimal import Decimal
from .tariffs import active

def collect(state, rows, history, now, localize, integrity):
    """Only confirmed hourly records from the first enabled observation onward."""
    tariff = active(history, localize(now).date())
    if state.get("start") is None:
        if not tariff or tariff["energy"] is None:
            return False
        state["start"] = now.replace(minute=0, second=0, microsecond=0).isoformat()
    changed = False
    records = state.setdefault("records", {})
    for when, row in rows.items():
        key = when.isoformat()
        if when < datetime.fromisoformat(state["start"]):
            continue
        if integrity(row, rows.get(when-timedelta(hours=1))) != "consistent":
            continue
        day = localize(when).date()
        old = records.get(key)
        rate = old["rate"] if old else None
        if old is None:
            t = active(history, day)
            if not t or t["energy"] is None:
                continue
            rate = t["energy"]
        value = {"day":day.isoformat(), "wh":row["consumption"], "rate":rate}
        if old != value:
            records[key] = value
            changed = True
    return changed

def summarize(state, history, today):
    if not state.get("start"):
        return {}
    records = list(state.get("records", {}).values())
    month = today.isoformat()[:7]
    current = [r for r in records if r["day"].startswith(month)]
    def cost(items):
        return sum((Decimal(str(r["wh"]))*Decimal(str(r["rate"]))/Decimal(1000000) for r in items), Decimal(0))
    energy = cost(current)
    wh = sum(r["wh"] for r in current)
    # Full calendar month fee estimate, weighted by effective tariff days.
    days = monthrange(today.year,today.month)[1]
    fees = [active(history,today.replace(day=d)) for d in range(1,days+1)]
    basic = None
    if all(t and t["basic"] is not None for t in fees):
        basic = sum((Decimal(str(t["basic"])) for t in fees),Decimal(0))/days
    else:
        t = active(history,today)
        if t and t["basic"] is not None:
            basic = Decimal(str(t["basic"]))
    total = energy + basic if basic is not None else None
    return {"accumulated_energy_cost":float(cost(records)), "monthly_energy_cost":float(energy),
            "monthly_basic_cost":float(basic) if basic is not None else None,
            "monthly_total_cost":float(total) if total is not None else None,
            "effective_energy_price":float(total*100000/Decimal(str(wh))) if total is not None and wh else None,
            "monthly_cost_hours":len(current), "monthly_cost_energy":wh/1000}
