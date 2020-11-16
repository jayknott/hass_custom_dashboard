"""Setup Custom Dashboard"""
from logging import Logger
from homeassistant.config_entries import ConfigEntry
import logging

from homeassistant import config_entries
from homeassistant.components.automation import EVENT_AUTOMATION_RELOADED
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Config, Event, HomeAssistant
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers.typing import ConfigType

from .automation import update_built_in_automations
from .counters import update_built_in_counters
from .files import update_files
from .input_boolean import update_built_in_input_boolean
from .input_number import update_built_in_input_number
from .input_select import update_built_in_input_select
from .input_text import update_built_in_input_text
from .lovelace import update_lovelace
from .registry import (
    setup_registries,
    update_area_registry,
    update_entity_registry,
    update_registries,
)

from .settings import (
    save_setting,
    SCHEMA_UPDATE_AREA_SERVICE,
    SCHEMA_UPDATE_ENTITY_SERVICE,
)
from .template import (
    setup_template,
    update_template_areas_global,
    update_template_entities_global,
)
from .yaml_parser import setup_yaml_parser
from .const import (
    CONF_ACTION,
    CONF_AREA,
    CONF_AREAS,
    CONF_BUILT_IN_ENTITIES,
    CONF_CREATE,
    CONF_ENTITIES,
    CONF_ENTITY,
    CONF_MISSING_RESOURCES,
    CONF_REMOVE,
    CONF_UPDATE,
    DOMAIN,
    # EVENT_MODULE_SETUP_COMPLETE,
    EVENT_SETTINGS_CHANGED,
    SERVICE_SET_AREA,
    SERVICE_SET_ENTITY,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)


async def component_setup(hass: HomeAssistant, config: ConfigType):
    # Check if legacy templates are enabled.
    if hass.config.legacy_templates:
        _LOGGER.error(
            f"Legacy templates are enabled. {TITLE} requires legacy templates to be disabled."
        )
        return False

    # Check for HACS
    if "hacs" not in hass.config.components:
        _LOGGER.error("HACS is not installed, Custom Dashboard cannot initiate.")
        return False

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

    async def handle_automation_reloaded(_event: Event):
        await update_built_in_automations(hass, True)

    async def handle_registry_updated(event: Event):
        await update_area_registry(hass)
        await update_template_areas_global(hass)

        action: str = event.data.get(CONF_ACTION)

        if action in [CONF_REMOVE]:
            pass
            # Remove area settings
            # Remove area id from entities settings

        if action in [CONF_REMOVE, CONF_UPDATE]:
            await update_entity_registry(hass)
            await update_template_entities_global(hass)

        if action in [CONF_CREATE, CONF_REMOVE]:
            await update_built_in_counters(hass)

        # trigger automations

    async def handle_area_registry_updated(event: Event):
        _LOGGER.warn(f"area updated::: {event}")
        await handle_registry_updated(event)

    async def handle_hass_started(_event: Event):
        await update_registries(hass)
        await update_template_areas_global(hass)
        await update_template_entities_global(hass)
        create_task(update_built_in_counters(hass))
        create_task(update_built_in_input_boolean(hass))
        create_task(update_built_in_input_number(hass))
        create_task(update_built_in_input_select(hass))
        create_task(update_built_in_input_text(hass))
        create_task(update_built_in_automations(hass))
        create_task(update_lovelace(hass, config))
        hass.bus.async_listen(EVENT_SETTINGS_CHANGED, handle_registry_updated)
        hass.bus.async_listen(EVENT_AUTOMATION_RELOADED, handle_automation_reloaded)
        hass.bus.async_listen(EVENT_AREA_REGISTRY_UPDATED, handle_area_registry_updated)
        hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, handle_registry_updated)
        hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, handle_registry_updated)

    if DOMAIN not in hass.config_entries.async_domains():
        await hass.config_entries.async_add(config_entries.ConfigEntry())

    create_task = hass.async_create_task
    await setup_registries(hass)
    create_task(update_files(hass))
    create_task(setup_template(hass))
    create_task(setup_yaml_parser(hass))

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_hass_started)

    async def service_save_area_setting(call):
        await save_setting(hass, CONF_AREA, call)

    async def service_save_entity_setting(call):
        await save_setting(hass, CONF_ENTITY, call)

    hass.services.async_register(
        DOMAIN, SERVICE_SET_AREA, service_save_area_setting, SCHEMA_UPDATE_AREA_SERVICE
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ENTITY,
        service_save_entity_setting,
        SCHEMA_UPDATE_ENTITY_SERVICE,
    )

    return True


async def async_setup(hass: HomeAssistant, config: ConfigType):
    return await component_setup(hass, config)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry):
    return await component_setup(hass, config.data)
