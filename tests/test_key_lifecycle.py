from datetime import date, timedelta
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("key_lifecycle", Path(__file__).resolve().parents[1] / "custom_components/salon_district_heating/key_lifecycle.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

@pytest.mark.parametrize("days,stage", [(None,None),(31,None),(30,"thirty_days"),(8,"thirty_days"),(7,"seven_days"),(2,"seven_days"),(1,"one_day"),(0,"expired"),(-1,"expired")])
def test_stage(days, stage):
    today = date(2026, 11, 26)
    expiry = (today + timedelta(days=days)).isoformat() if days is not None else None
    assert mod.days_remaining(expiry,today) == days
    assert mod.warning_stage(days) == stage

def test_normalize():
    assert mod.normalize_expiry("") is None
    assert mod.normalize_expiry("2028-11-23") == "2028-11-23"
    with pytest.raises(ValueError):
        mod.normalize_expiry("2028-02-30")
