import asyncio
import importlib
import json
from pathlib import Path
import sys
import types
from unittest.mock import AsyncMock, MagicMock
import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "salon_district_heating"

# Load the independent API module without importing the HA entry point.
package = types.ModuleType("test_salon_api")
package.__path__ = [str(COMPONENT)]
sys.modules[package.__name__] = package
api = importlib.import_module("test_salon_api.api")

def fixture(name):
    return json.loads((ROOT / "tests" / "fixtures" / name).read_text())

def response(status, payload):
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=types.SimpleNamespace(status=status, json=AsyncMock(return_value=payload)))
    context.__aexit__ = AsyncMock(return_value=False)
    return context

def test_locations():
    session = MagicMock()
    session.get.return_value = response(200, fixture("locations.json"))
    assert asyncio.run(api.Client(session, "fake").locations())[0]["id"] == 1

@pytest.mark.parametrize("status,error", [(401,api.AuthenticationError),(403,api.AuthenticationError),(429,api.RateLimitError),(500,api.ApiError)])
def test_errors(status,error):
    session = MagicMock()
    session.get.return_value = response(status,{})
    with pytest.raises(error):
        asyncio.run(api.Client(session,"fake").locations())

def test_external_pagination_rejected():
    session = MagicMock()
    session.get.return_value = response(200, {"results":[],"next":"https://example.org/steal"})
    with pytest.raises(api.ApiError):
        asyncio.run(api.Client(session,"fake").locations())
    assert session.get.call_count == 1

def test_consumptions():
    session = MagicMock()
    session.get.return_value = response(200,fixture("consumptions.json"))
    assert len(asyncio.run(api.Client(session,"fake").consumptions(1,"2026-01-01T00:00:00Z","2026-01-02T00:00:00Z"))) == 24

def keys(value):
    return { (key, sub) for key, item in value.items() for sub in (keys(item) if isinstance(item,dict) else {None}) }

def test_translation_parity():
    source = json.loads((COMPONENT / "strings.json").read_text())
    for language in ("en","fi","sv"):
        assert keys(source) == keys(json.loads((COMPONENT / "translations" / f"{language}.json").read_text()))
