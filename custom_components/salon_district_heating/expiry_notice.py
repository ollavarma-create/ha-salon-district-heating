"""Expiry notices are advisory and never stop polling."""
from homeassistant.core import callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util
from .const import DOMAIN
from .key_lifecycle import days_remaining, warning_stage

@callback
def clear_expiry_notice(hass, entry):
    for stage in ("thirty_days", "seven_days", "one_day", "expired"):
        ir.async_delete_issue(hass, DOMAIN, f"{entry.entry_id}_key_{stage}")

@callback
def setup_expiry_notice(hass, entry):
    @callback
    def check(_now=None):
        expiry = entry.data.get("api_key_expiry")
        stage = warning_stage(days_remaining(expiry, dt_util.now().date()))
        for other in ("thirty_days", "seven_days", "one_day", "expired"):
            if other != stage:
                ir.async_delete_issue(hass, DOMAIN, f"{entry.entry_id}_key_{other}")
        if stage:
            ir.async_create_issue(hass, DOMAIN, f"{entry.entry_id}_key_{stage}", is_fixable=False, severity=ir.IssueSeverity.WARNING, translation_key=f"key_{stage}", translation_placeholders={"expiry": expiry}, learn_more_url="https://lampovahti.salonkaukolampo.fi/login")
    check()
    entry.async_on_unload(async_track_time_change(hass, check, hour=0, minute=0, second=0))
