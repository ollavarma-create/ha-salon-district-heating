"""UI-only configuration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from .const import DOMAIN
from homeassistant.util import dt as dt_util
from .tariffs import active, upcoming, configure
from .key_lifecycle import normalize_expiry, reconfigured_expiry

def key_schema():
    return vol.Schema({vol.Required("api_key"): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)), vol.Optional("api_key_expiry"): selector.DateSelector()})
from .api import Client, ApiError, AuthenticationError

class SalonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return TariffOptionsFlow()

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
            return self.async_update_reload_and_abort(entry, data_updates={"api_key_expiry": reconfigured_expiry(user_input, entry.data.get("api_key_expiry"))}, reason="expiry_updated")
        schema = vol.Schema({vol.Optional("api_key_expiry"): selector.DateSelector(), vol.Optional("clear_expiry", default=False): selector.BooleanSelector()})
        return self.async_show_form(step_id="reconfigure", data_schema=self.add_suggested_values_to_schema(schema, entry.data))


class TariffOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        today = dt_util.now().date()
        history = self.config_entry.options.get("tariffs", [])
        errors = {}
        if user_input is not None:
            try:
                updated = configure(history, user_input, today)
            except (ValueError, TypeError, KeyError):
                errors["base"] = "invalid_tariff"
            else:
                self.hass.config_entries.async_update_entry(self.config_entry, options={**self.config_entry.options, "tariffs": updated})
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={**self.config_entry.options, "tariffs": updated})
        current = active(history,today) or {}
        future = upcoming(history,today) or {}
        number = selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=100000, step=0.01, mode=selector.NumberSelectorMode.BOX))
        schema = vol.Schema({
            vol.Required("enabled", default=current.get("energy") is not None): selector.BooleanSelector(),
            vol.Required("energy", default=current.get("energy") or 0): number,
            vol.Required("basic", default=current.get("basic") or 0): number,
            vol.Required("schedule", default=bool(future)): selector.BooleanSelector(),
            vol.Optional("next_date"): selector.DateSelector(),
            vol.Required("next_energy", default=future.get("energy") or 0): number,
            vol.Required("next_basic", default=future.get("basic") or 0): number,
        })
        return self.async_show_form(step_id="init", data_schema=self.add_suggested_values_to_schema(schema, {"next_date":future["date"]} if future else {}), errors=errors)
