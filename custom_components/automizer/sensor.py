from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry, ConfigType, DiscoveryInfoType
# from . import integrationStorage as storage

from homeassistant.const import UnitOfTemperature, UnitOfElectricPotential, PERCENTAGE


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    storage = hass.data["automizer"][config_entry.entry_id]
    async_add_entities(storage["binarySensors"])
    async_add_entities(storage["temperatureSensors"])
    async_add_entities(storage["humiditySensors"])
    async_add_entities(storage["textSensors"])
    async_add_entities(storage["analogSensors"])


class InelsBinarySensor(BinarySensorEntity):
    def __init__(self, inelsName, inelsId):
        self._attr_name = inelsName
        self._attr_is_on = False
        self._attr_unique_id = inelsName + inelsId
        self.inelsName = inelsName
        self.inelsId = inelsId
        self.ic = None

    @property
    def is_on(self):
        return self._attr_is_on

    def update(self):
        self.schedule_update_ha_state()
        # self._attr_is_on = not self._attr_is_on  # Alterna el estado para el ejemplo


class InelsTemperatureSensor(SensorEntity):
    def __init__(self, inelsName, inelsId, refreshSeconds=1):
        self._attr_name = inelsName
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        # self._attr_native_value = 77.7
        self._attr_unique_id = inelsName + inelsId
        self.inelsName = inelsName
        self.inelsId = inelsId
        self._attr_icon = "mdi:thermometer"
        self.ic = None
        self.refreshSeconds = refreshSeconds
        self.lastUpdate = 0

    @property
    def native_value(self):
        return self._attr_native_value

    def update(self):
        self.schedule_update_ha_state()
        # self._attr_native_value += 0.1


class InelsAnalogSensor(SensorEntity):
    def __init__(self, inelsName, inelsId, decimals=3, refreshSeconds=1):
        self._attr_name = inelsName
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
        self._attr_unique_id = inelsName + inelsId
        self.inelsName = inelsName
        self.inelsId = inelsId
        self._attr_icon = "mdi:gauge"
        self.decimals = decimals
        self.refreshSeconds = refreshSeconds
        self.lastUpdate = 0
        self.ic = None

    @property
    def native_value(self):
        return self._attr_native_value

    def update(self):
        self.schedule_update_ha_state()


class InelsHumiditySensor(SensorEntity):
    def __init__(self, inelsName, inelsId, refreshSeconds=1):
        self._attr_name = inelsName
        self._attr_native_unit_of_measurement = PERCENTAGE
        # self._attr_native_value = 77.7
        self._attr_unique_id = inelsName + inelsId
        self.inelsName = inelsName
        self.inelsId = inelsId
        self._attr_icon = "mdi:water-percent"
        self.ic = None
        self.refreshSeconds = refreshSeconds

    @property
    def native_value(self):
        return self._attr_native_value

    def update(self):
        self.schedule_update_ha_state()
        # self._attr_native_value += 0.1


class InelsTextSensor(SensorEntity):
    def __init__(self, inelsName, inelsId):
        self._attr_name = inelsName
        self._attr_native_value = "STOP"
        self._attr_unique_id = inelsName + inelsId
        self.inelsName = inelsName
        self.inelsId = inelsId
        self.ic = None

    @property
    def native_value(self):
        return self._attr_native_value

    def set_value(self):
        pass

    def update(self):
        self.schedule_update_ha_state()
        # self._attr_native_value = ("Updated Value")
