from homeassistant.helpers.entity import ToggleEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry, ConfigType, DiscoveryInfoType
# from . import integrationStorage as storage


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    storage = hass.data["automizer"][config_entry.entry_id]
    async_add_entities(storage["switches"])


class InelsSwitch(ToggleEntity):
    def __init__(
        self,
        inelsName,
        inelsId,
    ):
        self._attr_name = inelsName
        self._attr_unique_id = inelsName + inelsId
        self.inelsId = inelsId
        self.inelsName = inelsName
        self._state = False
        self.ic = None

    @property
    def is_on(self):
        return self._state

    def turn_on(self, **kwargs):
        self._state = True
        self.ic.sendLine("SET " + self.inelsId + " 1")
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        self._state = False
        self.ic.sendLine("SET " + self.inelsId + " 0")
        self.schedule_update_ha_state()

    def update(self):
        self.schedule_update_ha_state()
