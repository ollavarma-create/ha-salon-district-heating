"""Centralized retrieval and adaptive scheduling."""
from datetime import datetime, timedelta, timezone
import logging
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util
from .costs import collect
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_point_in_utc_time
from .api import ApiError, AuthenticationError
from .polling import next_poll, current_sample, consumption_integrity, consumption_view

_LOGGER = logging.getLogger(__name__)

def stamp(row):
    value = datetime.fromisoformat(row["date"])
    if value.tzinfo is None:
        raise ValueError("Missing timezone")
    return value.astimezone(timezone.utc)

class SalonCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client):
        super().__init__(hass, _LOGGER, name="Salon Kaukolämpö", config_entry=entry)
        self.client = client
        self.location_id = entry.data["location_id"]
        self.cancel_poll = None
        self.stopped = False
        self.first_seen = None
        self.last_stamp = None
        self.retries = 0
        self.pending_dates = set()
        self.integrity = None
        self.last_successful_request = None
        self.auth_status = None
        self.entry = entry
        self.cost_store = Store(hass, 1, f"salon_district_heating.costs.{entry.entry_id}")
        self.cost_state = {}

    async def load_costs(self):
        self.cost_state = await self.cost_store.async_load() or {}

    async def _async_update_data(self):
        now = datetime.now(timezone.utc)
        try:
            rows = await self.client.consumptions(self.location_id, (now-timedelta(hours=48)).isoformat(), now.isoformat())
            self.last_successful_request = datetime.now(timezone.utc)
            self.auth_status = "accepted"
            rows = [row for row in rows if row.get("location_id") == self.location_id and stamp(row) <= now]
            latest = max(rows, key=stamp) if rows else None
            if latest is None:
                raise UpdateFailed("No recent measurements")
            date = stamp(latest)
            if date != self.last_stamp:
                self.first_seen = now
                self.last_stamp = date
                self.retries = 0
            elif not current_sample(now, date) or self.integrity == "pending":
                self.retries += 1
            _LOGGER.debug("Measurement date=%s modified=%s first_seen=%s retries=%s", date, latest.get("modified_at"), self.first_seen, self.retries)
            by_date = {stamp(row): row for row in rows}
            before = self.cost_state.get("start")
            changed = collect(self.cost_state, by_date, self.entry.options.get("tariffs", []), now, dt_util.as_local, consumption_integrity)
            if changed or before != self.cost_state.get("start"):
                await self.cost_store.async_save(self.cost_state)
            previous = by_date.get(date - timedelta(hours=1))
            self.integrity = consumption_integrity(latest, previous)
            # Revisit previously pending rows using the overlapping query.
            for pending in tuple(self.pending_dates):
                row = by_date.get(pending)
                if row is None:
                    if pending < now - timedelta(hours=48):
                        self.pending_dates.discard(pending)
                    continue
                if consumption_integrity(row, by_date.get(pending - timedelta(hours=1))) == "consistent":
                    self.pending_dates.discard(pending)
                    _LOGGER.debug("Consumption completed date=%s observed_delay=%s", pending, now - pending)
            if self.integrity == "pending":
                self.pending_dates.add(date)
            _LOGGER.debug("Consumption integrity=%s pending_count=%s", self.integrity, len(self.pending_dates))
            # Keep raw API rows intact; expose the latest verified consumption separately.
            return {**latest, **consumption_view(by_date, now)}
        except AuthenticationError:
            self.auth_status = "rejected"
            self.stop()
            raise ConfigEntryAuthFailed("API key rejected; it may be expired, revoked or invalid") from None
        except (ApiError, ValueError, KeyError, TypeError):
            raise UpdateFailed("Measurement retrieval failed") from None

    def schedule(self):
        if self.stopped:
            return
        if self.cancel_poll:
            self.cancel_poll()
        now = datetime.now(timezone.utc)
        complete = self.last_update_success and self.last_stamp is not None and current_sample(now, self.last_stamp) and self.integrity == "consistent"
        self.cancel_poll = async_track_point_in_utc_time(self.hass, self._poll, next_poll(now, complete))

    async def _poll(self, _now):
        self.cancel_poll = None
        try:
            await self.async_refresh()
        finally:
            self.schedule()

    def stop(self):
        self.stopped = True
        if self.cancel_poll:
            self.cancel_poll()
            self.cancel_poll = None
