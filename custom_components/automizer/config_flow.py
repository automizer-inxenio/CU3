"""Config flow for the automizer integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import asyncio
import telnetlib3

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

# from .const import DOMAIN, CONF_EXPORT, CONF_CU_NAME, CONF_INSTALLER, CONF_SERIAL

from . import const as c
from . import utils as utils

from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

_LOGGER = logging.getLogger(__name__)
# haID = ""

WS_HEADERS_SELECTOR = TextSelector(
    TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True)
)


# TODO adjust the data schema to the data that you need
"""
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_INSTALLATION_NAME, "Name of the installation's location"
        ): str,
        vol.Required(CONF_SERIAL, None, "Serial number for: " + haID): str,
        vol.Required(CONF_CU_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT): int,
        vol.Required(CONF_EXPORT): WS_HEADERS_SELECTOR,
    }
)

STEP_USER_DATA_SCHEMA.schema[vol.Required(CONF_EXPORT)]
"""


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port

    async def test_connection(self):
        try:
            reader, writer = await asyncio.wait_for(
                telnetlib3.open_connection(self.host, self.port), timeout=5
            )
            writer.close()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    if not utils.testSerial(hass, data[c.CONF_SERIAL]):
        raise ValueError("Serial nunber is incorrect")

    hub = PlaceholderHub(data[CONF_HOST], data[CONF_PORT])
    if not await hub.test_connection():
        raise CannotConnect("Could not connect to cu host")

    if not data[c.CONF_CU_NAME]:
        raise ValueError("Must provide central unit name.")

    if not data[CONF_HOST]:
        raise ValueError("Must provide central unit host.")

    if not data[CONF_PORT]:
        raise ValueError("Must provide central unit port.")

    if not data[c.CONF_EXPORT]:
        raise ValueError("Must provide central unit export.")

    if not data[c.CONF_SERIAL]:
        raise ValueError("Must provide serial nunber")

    #    hub = PlaceholderHub(data[CONF_HOST], data[CONF_PORT])
    #    if not await hub.test_connection():
    #        return False
    # raise CannotConnect("Could not connect to cu host")

    return {
        "title": "Automizer "
        + data[c.CONF_CU_NAME]
        + " at "
        + data[CONF_HOST]
        + ":"
        + str(data[CONF_PORT])
    }


class ConfigFlow(ConfigFlow, domain=c.DOMAIN):
    """Handle a config flow for automizer."""

    #    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        haID = self.hass.data["core.uuid"]

        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(c.CONF_SERIAL, None, "Serial number for: " + haID): str,
                vol.Required(c.CONF_CU_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT): int,
                vol.Required(c.CONF_EXPORT): WS_HEADERS_SELECTOR,
            }
        )

        STEP_USER_DATA_SCHEMA.schema[vol.Required(c.CONF_EXPORT)]

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
