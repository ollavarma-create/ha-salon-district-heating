"""District heating measurements."""
from dataclasses import dataclass
from datetime import date
from homeassistant.util import dt as dt_util
from .key_lifecycle import days_remaining
from .costs import summarize
from .tariffs import active, upcoming, hourly_cost
from homeassistant.helpers.event import async_track_time_change
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import EntityCategory
from .const import DOMAIN
from .coordinator import stamp

@dataclass(frozen=True, kw_only=True)
class Description(SensorEntityDescription):
    field: str = ""
    scale: float = 1

TARIFF_KEYS = ("current_energy_tariff", "current_basic_fee", "next_energy_tariff", "next_basic_fee", "next_tariff_date")
COST_KEYS = ("accumulated_energy_cost","monthly_energy_cost","monthly_basic_cost","monthly_total_cost","effective_energy_price","monthly_cost_hours","monthly_cost_energy")
DESCRIPTIONS = (
    Description(key="accumulated_energy_cost", device_class=SensorDeviceClass.MONETARY, native_unit_of_measurement="EUR", suggested_display_precision=2),
    Description(key="monthly_energy_cost", device_class=SensorDeviceClass.MONETARY, native_unit_of_measurement="EUR", suggested_display_precision=2),
    Description(key="monthly_basic_cost", device_class=SensorDeviceClass.MONETARY, native_unit_of_measurement="EUR", suggested_display_precision=2),
    Description(key="monthly_total_cost", device_class=SensorDeviceClass.MONETARY, native_unit_of_measurement="EUR", suggested_display_precision=2),
    Description(key="effective_energy_price", native_unit_of_measurement="snt/kWh", suggested_display_precision=2),
    Description(key="monthly_cost_hours", native_unit_of_measurement="h", suggested_display_precision=0),
    Description(key="monthly_cost_energy", native_unit_of_measurement="kWh", suggested_display_precision=2),
    Description(key="current_energy_tariff", native_unit_of_measurement="€/kWh", suggested_display_precision=5),
    Description(key="current_basic_fee", native_unit_of_measurement="€/month", suggested_display_precision=2),
    Description(key="next_energy_tariff", native_unit_of_measurement="€/kWh", suggested_display_precision=5),
    Description(key="next_basic_fee", native_unit_of_measurement="€/month", suggested_display_precision=2),
    Description(key="next_tariff_date", device_class=SensorDeviceClass.DATE),
    Description(key="hourly_energy_cost", device_class=SensorDeviceClass.MONETARY, native_unit_of_measurement="EUR", suggested_display_precision=4),
    Description(key="api_key_expiry", device_class=SensorDeviceClass.DATE, entity_category=EntityCategory.DIAGNOSTIC),
    Description(key="api_key_days_remaining", native_unit_of_measurement="d", entity_category=EntityCategory.DIAGNOSTIC),
    Description(key="api_auth_status", device_class=SensorDeviceClass.ENUM, options=["accepted", "rejected"], entity_category=EntityCategory.DIAGNOSTIC),
    Description(key="last_successful_request", device_class=SensorDeviceClass.TIMESTAMP, entity_category=EntityCategory.DIAGNOSTIC),
    Description(key="energy_total", field="reading_total", scale=.001, device_class=SensorDeviceClass.ENERGY, native_unit_of_measurement="kWh", state_class=SensorStateClass.TOTAL_INCREASING),
    Description(key="hourly_energy", field="consumption", scale=.001, device_class=SensorDeviceClass.ENERGY, native_unit_of_measurement="kWh"),
    Description(key="average_power", field="consumption", scale=.001, device_class=SensorDeviceClass.POWER, native_unit_of_measurement="kW"),
    Description(key="supply_temperature", field="flow_temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement="°C", state_class=SensorStateClass.MEASUREMENT),
    Description(key="return_temperature", field="return_temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement="°C", state_class=SensorStateClass.MEASUREMENT),
    Description(key="temperature_difference", native_unit_of_measurement="K", state_class=SensorStateClass.MEASUREMENT),
    Description(key="flow", field="flow", suggested_display_precision=3, device_class=SensorDeviceClass.VOLUME_FLOW_RATE, native_unit_of_measurement="m³/h", state_class=SensorStateClass.MEASUREMENT),
    Description(key="measurement_time", device_class=SensorDeviceClass.TIMESTAMP),
    Description(key="consumption_time", device_class=SensorDeviceClass.TIMESTAMP, entity_category=EntityCategory.DIAGNOSTIC),
    Description(key="data_quality", field="data_quality", device_class=SensorDeviceClass.ENUM, options=["confirmed", "pending", "stale", "unverifiable"], entity_category=EntityCategory.DIAGNOSTIC),
    Description(key="reading_status", field="status", device_class=SensorDeviceClass.ENUM, options=["read", "estimated"]),
)

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(SalonSensor(entry.runtime_data, entry, description) for description in DESCRIPTIONS)

class SalonSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator)
        self.entry = entry
        self.entity_description = description
        self._attr_translation_key = description.key
        self._attr_unique_id = f'{entry.data["location_id"]}_{description.key}'
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, str(entry.data["location_id"]))}, name="Salon Kaukolämpö", manufacturer="Salon Kaukolämpö")

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if self.entity_description.key in TARIFF_KEYS + COST_KEYS:
            self.async_on_remove(async_track_time_change(self.hass, self._tariff_midnight, hour=0, minute=0, second=0))

    async def _tariff_midnight(self, now):
        self.async_write_ha_state()

    @property
    def available(self):
        if self.entity_description.key in TARIFF_KEYS + COST_KEYS:
            return True
        if self.entity_description.key in ("api_key_expiry", "api_key_days_remaining", "api_auth_status", "last_successful_request"):
            return True
        return super().available

    @property
    def native_value(self):
        key = self.entity_description.key
        history = self.entry.options.get("tariffs", [])
        if key in COST_KEYS:
            if (active(history, dt_util.now().date()) or {}).get("energy") is None:
                return None
            return summarize(self.coordinator.cost_state, history, dt_util.now().date()).get(key)
        if key in TARIFF_KEYS:
            today = dt_util.now().date()
            tariff = upcoming(history,today) if key.startswith("next_") else active(history,today)
            if not tariff:
                return None
            if key == "next_tariff_date":
                return date.fromisoformat(tariff["date"])
            value = tariff["energy" if "energy" in key else "basic"]
            return value / 1000 if value is not None and "energy" in key else value
        if key == "hourly_energy_cost":
            row = self.coordinator.data or {}
            when = row.get("consumption_time")
            return hourly_cost(row.get("consumption"), active(history, dt_util.as_local(when).date())) if when else None
        expiry = self.entry.data.get("api_key_expiry")
        if key == "api_key_expiry":
            return date.fromisoformat(expiry) if expiry else None
        if key == "api_key_days_remaining":
            return days_remaining(expiry, dt_util.now().date())
        if key == "api_auth_status":
            return self.coordinator.auth_status
        if key == "last_successful_request":
            return self.coordinator.last_successful_request
        row = self.coordinator.data
        if not row:
            return None
        desc = self.entity_description
        if desc.key == "measurement_time":
            return stamp(row)
        if desc.key == "consumption_time":
            return row.get("consumption_time")
        if desc.key == "temperature_difference":
            a, b = row.get("flow_temperature"), row.get("return_temperature")
            return round(a-b, 2) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else None
        value = row.get(desc.field)
        if desc.key in ("reading_status", "data_quality"):
            return value if value in desc.options else None
        return round(value * desc.scale, 6) if isinstance(value,(int,float)) and not isinstance(value,bool) else None
