"""
Custom Dashboard automatically sets up everything needed for a custom Lovelace experience

For more details about this integration, please refer to the documentation at
https://github.com/jayknott/custom_dashboard
"""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .setup import (
    async_setup as yaml_setup,
    async_setup_entry as ui_setup,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: {}}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up this integration using yaml."""

    return await yaml_setup(hass, config)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigType):
    """Set up this integration using UI."""

    return await ui_setup(hass, config_entry)