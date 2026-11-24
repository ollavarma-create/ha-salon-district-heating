from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("polling", Path(__file__).resolve().parents[1] / "custom_components/salon_district_heating/polling.py")
polling = importlib.util.module_from_spec(spec)
spec.loader.exec_module(polling)

@pytest.mark.parametrize("minute,complete,hour,target", [(0,False,10,20),(21,False,10,30),(31,False,10,40),(41,False,10,50),(51,False,11,20),(21,True,11,20)])
def test_schedule(minute,complete,hour,target):
    now = datetime(2026,1,1,10,minute,tzinfo=timezone.utc)
    result = polling.next_poll(now,complete)
    assert (result.hour,result.minute) == (hour,target)
    assert 0 <= result.second <= 30

def test_current_sample():
    now = datetime(2026,1,1,10,20,tzinfo=timezone.utc)
    assert polling.current_sample(now,now.replace(minute=0))
    assert not polling.current_sample(now,now.replace(hour=9,minute=0))
