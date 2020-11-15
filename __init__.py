import logging
import voluptuous as vol

from .const import DOMAIN
from .setup import (
    async_setup as yaml_setup,
    async_setup_entry as ui_setup,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: None}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up this integration using yaml."""

    return await yaml_setup(hass, config)


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""

    return await ui_setup(hass, config_entry)