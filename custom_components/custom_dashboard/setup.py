"""Setup the integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .components.automation import update_built_in_automations
from .components.counters import setup_counters
from .components.input_boolean import setup_input_booleans
from .components.input_number import update_built_in_input_number
from .components.input_select import update_built_in_input_select
from .components.input_text import update_built_in_input_text
from .components.lovelace import update_lovelace
from .components.registry import setup_registries, update_registries
from .components.yaml_parser import setup_yaml_parser
from .events import setup_events
from .files import setup_files

from .services import setup_services
from .components.template import (
    setup_template,
    update_template_areas_global,
    update_template_entities_global,
)

from .const import (
    CONF_AREAS,
    CONF_BUILT_IN_ENTITIES,
    CONF_ENTITIES,
    CONF_MISSING_RESOURCES,
    DOMAIN,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)


async def setup_integration(hass: HomeAssistant, config: ConfigType) -> bool:
    """Main setup procedure for this integration."""

    # Check if legacy templates are enabled.
    if hass.config.legacy_templates:
        _LOGGER.error(
            f"Legacy templates are enabled. {TITLE} requires legacy templates to be disabled."
        )
        return False

    # Check for HACS
    if "hacs" not in hass.config.components:
        _LOGGER.warning(
            f"HACS is not installed, {TITLE} dependencies will have to be installed manually."
        )

    # Check for browser mod.
    if "browser_mod" not in hass.config.components:
        _LOGGER.warning(
            f"Key 'browser_mod' not found in configuration.yaml. Browser mod is required for popups and other UI elements."
        )

    hass.data[DOMAIN] = {
        CONF_BUILT_IN_ENTITIES: {},
        CONF_MISSING_RESOURCES: [],
        CONF_AREAS: [],
        CONF_ENTITIES: [],
    }

    async def handle_hass_started(_event: Event) -> None:
        """Event handler for when HA has started."""

        await update_registries(hass)
        await update_template_areas_global(hass)
        await update_template_entities_global(hass)
        create_task(setup_counters(hass))
        create_task(setup_input_booleans(hass))
        create_task(update_built_in_input_number(hass))
        create_task(update_built_in_input_select(hass))
        create_task(update_built_in_input_text(hass))
        create_task(update_built_in_automations(hass))
        create_task(update_lovelace(hass, config))
        create_task(setup_events(hass))
        create_task(setup_services(hass))

    await setup_registries(hass)

    create_task = hass.async_create_task
    create_task(setup_files(hass))
    create_task(setup_template(hass))
    create_task(setup_yaml_parser(hass))

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_hass_started)

    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up this integration using yaml."""

    return await setup_integration(hass, config)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up this integration using the UI."""

    return await setup_integration(hass, config.data)
