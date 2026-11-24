"""Salon district heating integration."""
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import Client, ApiError, AuthenticationError

async def async_setup_entry(hass, entry):
    client = Client(async_get_clientsession(hass), entry.data["api_key"])
    try:
        locations = await client.locations()
    except AuthenticationError:
        raise ConfigEntryAuthFailed("Authentication failed") from None
    except ApiError:
        raise ConfigEntryNotReady("API unavailable") from None
    if not any(row["id"] == entry.data["location_id"] for row in locations):
        raise ConfigEntryAuthFailed("Location inaccessible")
    entry.runtime_data = client
    return True

async def async_unload_entry(hass, entry):
    return True

