"""Setup the integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .components.automation import setup_automations
from .components.counters import setup_counters
from .components.input_boolean import setup_input_booleans
from .components.input_number import setup_input_numbers
from .components.input_select import setup_input_selects
from .components.input_text import setup_input_texts
from .components.lovelace import lovelace_mode, setup_lovelace
from .components.registry import setup_registries, update_registries
from .components.template import (
    setup_template,
    update_template_areas_global,
    update_template_entities_global,
)
from .components.yaml_parser import setup_yaml_parser
from .events import setup_events
from .files import setup_files
from .model import Configuration
from .share import get_base
from .services import setup_services


from .const import DOMAIN, TITLE

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

    base = get_base()
    base.hass = hass

    # hass.data[DOMAIN] = {
    #     CONF_BUILT_IN_ENTITIES: {},
    #     CONF_MISSING_RESOURCES: [],
    #     CONF_AREAS: [],
    #     CONF_ENTITIES: [],
    # }

    async def handle_hass_started(_event: Event) -> None:
        """Event handler for when HA has started."""

        await update_registries()
        await update_template_areas_global()
        await update_template_entities_global()
        create_task(setup_counters())
        create_task(setup_input_booleans())
        create_task(setup_input_numbers())
        create_task(setup_input_selects())
        create_task(setup_input_texts())
        create_task(setup_automations())
        create_task(setup_lovelace())
        create_task(setup_events())
        create_task(setup_services())

    await setup_registries()

    create_task = hass.async_create_task
    create_task(setup_files())
    create_task(setup_template())
    create_task(setup_yaml_parser())

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_hass_started)

    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up this integration using yaml."""

    base = get_base()
    base.configuration = (
        base.configuration if base.configuration is not None else Configuration()
    )
    base.configuration.lovelace_mode = lovelace_mode(config)

    if DOMAIN not in config:
        return True

    if base.configuration and base.configuration.config_type == "flow":
        return True

    base.configuration.config = config[DOMAIN]
    base.configuration.config_type = "yaml"

    return await setup_integration(hass, config)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up this integration using the UI."""

    base = get_base()

    if base.configuration and base.configuration.config_type == "yaml":
        base.log.warning(
            f"""
                {TITLE} is setup both in config.yaml and integrations.
                The YAML configuration has taken precedence.
            """
        )
        return False

    # Todo: Find out what this means and if it is needed.
    # if config_entry.source == config_entries.SOURCE_IMPORT:
    #     hass.async_create_task(hass.config_entries.async_remove(config_entry.entry_id))
    #     return False

    base.configuration = (
        base.configuration if base.configuration is not None else Configuration()
    )
    base.configuration.config_entry = config_entry
    base.configuration.config_type = "flow"

    return await setup_integration(hass, config_entry.data)
