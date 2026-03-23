from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
import voluptuous as vol

from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from . import const as c

WS_HEADERS_SELECTOR = TextSelector(
    TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True)
)


class AutomizerOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # self.config_entry es inyectado automáticamente por HA
        current = {**self.config_entry.data, **self.config_entry.options}

        ha_id = self.hass.data["core.uuid"]

        return self.async_show_form(
            step_id="init",
            description_placeholders={"ha_id": ha_id},
            data_schema=vol.Schema(
                {
                    vol.Required(c.CONF_SERIAL, default=current.get(c.CONF_SERIAL, "")): str,
                    vol.Required(CONF_HOST, default=current.get(CONF_HOST, "")): str,
                    vol.Required(CONF_PORT, default=current.get(CONF_PORT, 1111)): int,
                    vol.Required(c.CONF_CU_NAME, default=current.get(c.CONF_CU_NAME, "")): str,
                    vol.Required(c.CONF_EXPORT, default=current.get(c.CONF_EXPORT, "")): WS_HEADERS_SELECTOR,
                }
            ),
        )
