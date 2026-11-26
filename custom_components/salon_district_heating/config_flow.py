"""UI-only configuration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from .const import DOMAIN
from .key_lifecycle import normalize_expiry

def key_schema():
    return vol.Schema({vol.Required("api_key"): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)), vol.Optional("api_key_expiry"): selector.DateSelector()})
from .api import Client, ApiError, AuthenticationError

class SalonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._key = user_input["api_key"].strip()
            self._expiry = normalize_expiry(user_input.get("api_key_expiry"))
            try:
                self._locations = await Client(async_get_clientsession(self.hass), self._key).locations()
                if self._locations:
                    return await self.async_step_location()
                errors["base"] = "no_locations"
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="user", data_schema=key_schema(), errors=errors)

    async def async_step_location(self, user_input=None):
        choices = {str(row["id"]): f'{row["name"]} ({row["id"]})' for row in self._locations}
        if user_input is not None:
            location = user_input["location_id"]
            if location in choices:
                await self.async_set_unique_id(location)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=choices[location], data={"api_key": self._key, "location_id": int(location), "api_key_expiry": self._expiry})
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
                    return self.async_update_reload_and_abort(entry, data_updates={"api_key": key, "api_key_expiry": normalize_expiry(user_input.get("api_key_expiry"))})
                errors["base"] = "no_locations"
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="reauth_confirm", data_schema=key_schema(), errors=errors)


    async def async_step_reconfigure(self, user_input=None):
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            return self.async_update_reload_and_abort(entry, data_updates={"api_key_expiry": normalize_expiry(user_input.get("api_key_expiry"))})
        schema = vol.Schema({vol.Optional("api_key_expiry"): selector.DateSelector()})
        return self.async_show_form(step_id="reconfigure", data_schema=self.add_suggested_values_to_schema(schema, entry.data))
