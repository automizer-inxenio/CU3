from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    LightEntityFeature,
    ATTR_BRIGHTNESS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry, ConfigType, DiscoveryInfoType

# from . import integrationStorage as storage
from . import utils as utils


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    storage = hass.data["automizer"][config_entry.entry_id]
    async_add_entities(storage["lights"])


class InelsLight(LightEntity):
    def __init__(self, inelsName, inelsId):
        self._attr_name = inelsName
        self._attr_unique_id = inelsName + inelsId
        self.inelsName = inelsName
        self.inelsId = inelsId
        self._state = False
        self._brightness = 255
        self.ic = None

    @property
    def is_on(self):
        """Devuelve True si la luz está encendida."""
        return self._state

    def turn_on(self, **kwargs) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
            controlLine = (
                "SET "
                + self.inelsId
                + " "
                + str(utils.scaleValue2550(int(self._brightness)))
            )
            self.ic.sendLine(controlLine)
            self._state = True
        else:
            controlLine = (
                "SET "
                + self.inelsId
                + " "
                + str(utils.scaleValue2550(int(self._brightness)))
            )
            self.ic.sendLine(controlLine)
            self._state = True

    def turn_off(self, **kwargs) -> None:
        self.ic.sendLine("SET " + self.inelsId + " 0")
        self._state = False

    def update(self):
        self.schedule_update_ha_state()
        return

    @property
    def brightness(self):
        return self._brightness

    @property
    def supported_color_modes(self):
        return {ColorMode.BRIGHTNESS}

    @property
    def color_mode(self):
        return ColorMode.BRIGHTNESS
