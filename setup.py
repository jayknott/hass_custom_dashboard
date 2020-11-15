from custom_components.custom_dashboard.automation import update_built_in_automations
import logging

from homeassistant import config_entires
from homeassistant.components.automation import EVENT_AUTOMATION_RELOADED
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED

from .binary_sensor import update_built_in_binary_sensors

# from .automation import update_built_in_automations
from .counters import update_built_in_counters
from .files import update_files
from .input_boolean import update_built_in_input_boolean
from .input_number import update_built_in_input_number
from .input_select import update_built_in_input_select
from .input_text import update_built_in_input_text
from .lovelace import update_lovelace
# from .settings import save_setting, SCHEMA_UPDATE_AREA_SERVICE, SCHEMA_UPDATE_ENTITY_SERVICE
from .template import setup_template, update_template_areas_global, update_template_entities_global
from .yaml_parser import setup_yaml_parser
from .const import (
    CONF_ACTION,
    # CONF_AREA,
    CONF_BUILT_IN_ENTITIES, CONF_CREATE,
    # CONF_ENTITY,
    CONF_MISSING_RESOURCES, CONF_REMOVE, CONF_UPDATE,
    DOMAIN,
    # EVENT_MODULE_SETUP_COMPLETE,
    EVENT_SETTINGS_CHANGED,
    # SERVICE_SET_AREA,
    # SERVICE_SET_ENTITY,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    # Check if legacy templates are enabled.
    if hass.config.legacy_templates:
        _LOGGER.error(f"Legacy templates are enabled. {TITLE} requires legacy templates to be disabled.")
        return False

    # Check for browser mod.
    if 'browser_mod' not in config.keys():
        _LOGGER.warning(f"Key 'browser_mod' not found in configuration.yaml. Browser mod is required for popups and other UI elements.")

    hass.data[DOMAIN] = {
        CONF_BUILT_IN_ENTITIES: {},
        CONF_MISSING_RESOURCES: [],
    }

    async def handle_automation_reloaded(_event=None):
        await update_built_in_automations(hass, True)

    async def handle_registry_updated(event=None):
        await update_template_areas_global(hass)
        
        action = event.data[CONF_ACTION]

        if action in [CONF_REMOVE]:
            pass
            # Remove area settings
            # Remove area id from entities settings

        if action in [CONF_REMOVE, CONF_UPDATE]:
            await update_template_entities_global(hass)

        if action in [CONF_CREATE, CONF_REMOVE]:
            await update_built_in_counters(hass)

        # trigger automations

    async def handle_area_registry_updated(event):
        _LOGGER.warn(f"area updated::: {event}")
        await handle_registry_updated()

    async def handle_hass_started(_event=None):
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
        await hass.config_entires.async_add(hass.config_entries.ConfigEntry(
            
        ))

    create_task = hass.async_create_task
    create_task(update_files(hass))
    create_task(setup_template(hass))
    create_task(setup_yaml_parser(hass))

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_hass_started)

    # async def service_save_area_setting(call):
    #     create_task(save_setting(hass, CONF_AREA, call))

    # async def service_save_entity_setting(call):
    #     create_task(save_setting(hass, CONF_ENTITY, call))

    # hass.services.async_register(
    #     DOMAIN, SERVICE_SET_AREA, service_save_area_setting, SCHEMA_UPDATE_AREA_SERVICE
    # )
    # hass.services.async_register(
    #     DOMAIN, SERVICE_SET_ENTITY, service_save_entity_setting, SCHEMA_UPDATE_ENTITY_SERVICE
    # )

    return True
