import logging

from homeassistant.components.automation import EVENT_AUTOMATION_RELOADED
from homeassistant.const import (
    ATTR_AREA_ID,
    ATTR_ID,
    ATTR_NAME,
    CONF_DEFAULT,
    CONF_ENTITY_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_TYPE,
)
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED

from .automation import update_built_in_automations
from .counters import update_built_in_counters
from .registry import update_area_registry, update_entity_registry
from .template import update_template_areas_global, update_template_entities_global
from .const import (
    BINARY_SENSOR_CLASS_MAP,
    CONF_ACTION,
    CONF_AREAS,
    CONF_CREATE,
    CONF_ENTITIES,
    CONF_ORIGINAL_AREA_ID,
    CONF_ORIGINAL_NAME,
    CONF_ORIGINAL_TYPE,
    CONF_REMOVE,
    CONF_SORT_ORDER,
    CONF_UPDATE,
    CONF_VISIBLE,
    COVER_CLASS_MAP,
    DEFAULT_ROOM_ICON,
    DEFAULT_SORT_ORDER,
    DOMAIN,
    EVENT_SETTINGS_CHANGED,
    PLATFORM_BINARY_SENSOR,
    PLATFORM_MAP,
    SENSOR_CLASS_MAP,
)

_LOGGER = logging.getLogger(__name__)


async def setup_events(hass: HomeAssistant):
    async def handle_automation_reloaded(_event: Event):
        await update_built_in_automations(hass, True)

    async def handle_registry_updated(event: Event):
        await update_area_registry(hass)
        await update_template_areas_global(hass)
        await update_entity_registry(hass)
        await update_template_entities_global(hass)

    async def handle_area_registry_updated(event: Event):
        await handle_update_area(hass, event)

    hass.bus.async_listen(EVENT_SETTINGS_CHANGED, handle_registry_updated)
    hass.bus.async_listen(EVENT_AUTOMATION_RELOADED, handle_automation_reloaded)
    hass.bus.async_listen(EVENT_AREA_REGISTRY_UPDATED, handle_area_registry_updated)
    hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, handle_registry_updated)
    hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, handle_registry_updated)


async def handle_update_area(hass: HomeAssistant, event: Event):
    _LOGGER.warn(event)
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