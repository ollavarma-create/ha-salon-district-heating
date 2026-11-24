"""UI-only configuration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from .const import DOMAIN
from .api import Client, ApiError, AuthenticationError

class SalonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._key = user_input["api_key"].strip()
            try:
                self._locations = await Client(async_get_clientsession(self.hass), self._key).locations()
                if self._locations:
                    return await self.async_step_location()
                errors["base"] = "no_locations"
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required("api_key"): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD))}), errors=errors)

    async def async_step_location(self, user_input=None):
        choices = {str(row["id"]): f'{row["name"]} ({row["id"]})' for row in self._locations}
        if user_input is not None:
            location = user_input["location_id"]
            if location in choices:
                await self.async_set_unique_id(location)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=choices[location], data={"api_key": self._key, "location_id": int(location)})
        return self.async_show_form(step_id="location", data_schema=vol.Schema({vol.Required("location_id"): vol.In(choices)}))

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        if user_input is not None:
            entry = self._get_reauth_entry()
            key = user_input["api_key"].strip()
            try:
                rows = await Client(async_get_clientsession(self.hass), key).locations()
                if any(row["id"] == entry.data["location_id"] for row in rows):
                    return self.async_update_reload_and_abort(entry, data_updates={"api_key": key})
                errors["base"] = "no_locations"
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="reauth_confirm", data_schema=vol.Schema({vol.Required("api_key"): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD))}), errors=errors)

