from homeassistant import config_entries
import voluptuous as vol


class AutomizerOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Aquí defines los campos que quieres permitir reconfigurar
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "host", default=self.config_entry.data.get("host", "")
                    ): str,
                    vol.Required(
                        "port", default=self.config_entry.data.get("port", 1234)
                    ): int,
                    # ...otros campos...
                }
            ),
        )
