from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from . import integrationStorage as storage


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    storage = hass.data["automizer"][config_entry.entry_id]
    async_add_entities(storage["numbers"])


class InelsNumber(NumberEntity):
    """Representación de un número con decimales configurables."""

    def __init__(self, inelsName, inelsId, decimals=2):
        self._attr_name = inelsName
        self._attr_native_step = 1 / (10**decimals)
        self._attr_native_min_value = -10000
        self._attr_native_max_value = 10000
        self._attr_native_value = 20.0
        self._attr_unique_id = inelsName + inelsId
        self.inelsName = inelsName
        self.inelsId = inelsId
        self.decimals = decimals
        self.ic = None

    def set_native_value(self, value: float) -> None:
        """Establece el valor del número."""
        self._attr_native_value = round(value, self.decimals)
        self.ic.sendLine("SET " + self.inelsId + " " + str(self._attr_native_value))
        self.schedule_update_ha_state()

    def update(self):
        """Actualiza el estado de la entidad."""
        self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Añadir atributos personalizados al estado."""
        return {"decimals": self.decimals}
