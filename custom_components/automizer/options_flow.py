from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
import voluptuous as vol

from . import const as c

WS_HEADERS_SELECTOR = TextSelector(
    TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True)
)


class AutomizerOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        haID = self.hass.data["core.uuid"]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        c.CONF_SERIAL, default=data.get(c.CONF_SERIAL, "")
                    ): str,
                    vol.Required(
                        c.CONF_CU_NAME, default=data.get(c.CONF_CU_NAME, "")
                    ): str,
                    vol.Required(CONF_HOST, default=data.get(CONF_HOST, "")): str,
                    vol.Required(CONF_PORT, default=data.get(CONF_PORT, 1234)): int,
                    vol.Required(
                        c.CONF_EXPORT, default=data.get(c.CONF_EXPORT, "")
                    ): WS_HEADERS_SELECTOR,
                }
            ),
            description_placeholders={"installation_id": haID},
        )
