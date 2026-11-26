from datetime import date
import importlib.util
from pathlib import Path
import pytest
spec = importlib.util.spec_from_file_location("tariffs", Path(__file__).resolve().parents[1] / "custom_components/salon_district_heating/tariffs.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def test_switch():
    today = date(2026,11,26)
    h = m.configure([], dict(enabled=True,energy=75.94,basic=34.05,schedule=True,next_date="2027-01-01",next_energy=79.69,next_basic=34.73),today)
    assert m.active(h,date(2026,12,31))["energy"] == 75.94
    assert m.active(h,date(2027,1,1))["energy"] == 79.69
    assert m.upcoming(h,date(2027,1,1)) is None
    assert m.hourly_cost(2000,m.active(h,today)) == .15188
    assert m.hourly_cost(2000,m.active(h,date(2027,1,1))) == .15938
    assert m.hourly_cost(None,m.active(h,today)) is None
    assert m.hourly_cost(2000,None) is None
    assert m.active(h,date(2026,11,25)) is None
    assert m.active(m.configure(h,dict(enabled=False),date(2027,1,2)),date(2027,1,1))["energy"] == 79.69
@pytest.mark.parametrize("value",[-1,float("nan"),float("inf")])
def test_invalid(value):
    with pytest.raises(ValueError):
        m.price(value)
