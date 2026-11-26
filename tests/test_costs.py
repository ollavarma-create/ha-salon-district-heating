import importlib.util
import sys
import types
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pytest

root = Path(__file__).resolve().parents[1] / "custom_components/salon_district_heating"
pkg = types.ModuleType("cost_test_package")
pkg.__path__ = [str(root)]
sys.modules[pkg.__name__] = pkg
from cost_test_package.costs import collect, summarize

def test_ledger():
    now = datetime(2026,11,26,10,tzinfo=timezone.utc)
    h = [{"date":"2026-11-01","energy":75.94,"basic":34.05}]
    s = {}
    rows = {now:{"consumption":2000}}
    ok = lambda a,b:"consistent"
    assert collect(s,rows,h,now,lambda x:x,ok)
    assert not collect(s,rows,h,now,lambda x:x,ok)
    assert summarize(s,h,now.date())["monthly_energy_cost"] == pytest.approx(.15188)
    rows[now]["consumption"] = 3000
    assert collect(s,rows,h,now,lambda x:x,ok)
    assert summarize(s,h,now.date())["monthly_cost_hours"] == 1
    assert summarize(s,h,now.date())["monthly_energy_cost"] == pytest.approx(.22782)
    assert not collect(s,{now-timedelta(hours=1):{"consumption":1000}},h,now,lambda x:x,ok)
    assert not collect(s,{now+timedelta(hours=1):{"consumption":1000}},h,now,lambda x:x,lambda a,b:"pending")
