"""Calendar-based API key expiry helpers."""
from datetime import date

def normalize_expiry(value):
    return date.fromisoformat(value).isoformat() if value else None

def days_remaining(value, today):
    return (date.fromisoformat(value) - today).days if value else None

def warning_stage(days):
    if days is None or days > 30:
        return None
    if days <= 0:
        return "expired"
    if days <= 1:
        return "one_day"
    if days <= 7:
        return "seven_days"
    return "thirty_days"


def reconfigured_expiry(user_input, previous):
    """Explicit removal takes precedence; omitted date preserves existing value."""
    if user_input.get("clear_expiry"):
        return None
    return normalize_expiry(user_input.get("api_key_expiry") or previous)
