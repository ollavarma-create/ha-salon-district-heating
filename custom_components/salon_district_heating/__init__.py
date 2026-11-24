"""Salon district heating integration."""
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import Client
from .coordinator import SalonCoordinator

async def async_setup_entry(hass, entry):
    coordinator = SalonCoordinator(hass, entry, Client(async_get_clientsession(hass), entry.data["api_key"]))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    coordinator.schedule()
    entry.async_on_unload(coordinator.stop)
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
