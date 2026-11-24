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

def test_delayed_consumption_same_modified_at():
    previous = {"serial_number": "synthetic", "reading_total": 10000}
    latest = {"serial_number": "synthetic", "reading_total": 11000,
              "consumption": 0, "modified_at": "2026-01-01T10:15:00Z"}
    assert polling.consumption_integrity(latest, previous) == "pending"
    corrected = {**latest, "consumption": 1000}
    assert polling.consumption_integrity(corrected, previous) == "consistent"
    assert latest["consumption"] == 0
    assert corrected["modified_at"] == latest["modified_at"]

@pytest.mark.parametrize("total,consumption,serial,expected", [
    (10000, 0, "synthetic", "consistent"),
    (11000, 2000, "synthetic", "pending"),
    (11000, None, "synthetic", "pending"),
    (11000, True, "synthetic", "pending"),
    (9000, 1000, "synthetic", "unverifiable"),
    (11000, 1000, "replacement", "unverifiable"),
    (None, 1000, "synthetic", "unverifiable"),
])
def test_integrity_edge_cases(total, consumption, serial, expected):
    previous = {"serial_number": "synthetic", "reading_total": 10000}
    latest = {"serial_number": serial, "reading_total": total, "consumption": consumption}
    assert polling.consumption_integrity(latest, previous) == expected

def test_missing_previous():
    assert polling.consumption_integrity({"consumption": 1000}, None) == "unverifiable"
