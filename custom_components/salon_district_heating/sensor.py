"""District heating measurements."""
from dataclasses import dataclass
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

DESCRIPTIONS = (
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
        self.entity_description = description
        self._attr_translation_key = description.key
        self._attr_unique_id = f'{entry.data["location_id"]}_{description.key}'
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, str(entry.data["location_id"]))}, name="Salon Kaukolämpö", manufacturer="Salon Kaukolämpö")

    @property
    def native_value(self):
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
