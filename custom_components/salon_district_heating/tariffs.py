"""Local calendar tariff schedule; prices include VAT."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import math

def price(value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("Invalid price")
    return value

def active(history, day):
    return max((r for r in history if r["date"] <= day.isoformat()), key=lambda r:r["date"], default=None)

def upcoming(history, day):
    return min((r for r in history if r["date"] > day.isoformat()), key=lambda r:r["date"], default=None)

def configure(history, values, today):
    if not values.get("enabled"):
        return [r for r in history if r["date"] < today.isoformat()] + [{"date":today.isoformat(),"energy":None,"basic":None}]
    current = {"date":today.isoformat(),"energy":price(values["energy"]),"basic":price(values["basic"])}
    old = active(history,today)
    result = [r for r in history if r["date"] <= today.isoformat()]
    if not old or any(old[k] != current[k] for k in ("energy","basic")):
        result = [r for r in result if r["date"] != current["date"]] + [current]
    if values.get("schedule"):
        day = date.fromisoformat(values["next_date"])
        if day <= today:
            raise ValueError("Future date required")
        result.append({"date":day.isoformat(),"energy":price(values["next_energy"]),"basic":price(values["next_basic"])})
    return result

def hourly_cost(wh, tariff):
    if wh is None or not tariff or tariff["energy"] is None:
        return None
    return float((Decimal(str(wh))*Decimal(str(tariff["energy"]))/Decimal(1000000)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
