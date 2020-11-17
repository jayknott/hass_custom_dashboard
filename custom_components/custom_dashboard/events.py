import logging

from homeassistant.components.automation import EVENT_AUTOMATION_RELOADED
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED

from .components.automation import update_built_in_automations
from .components.counters import update_counters
from .components.registry import update_area_registry, update_entity_registry
from .components.template import (
    update_template_areas_global,
    update_template_entities_global,
)
from .const import (
    CONF_ACTION,
    CONF_CREATE,
    CONF_REMOVE,
    CONF_UPDATE,
    EVENT_SETTINGS_CHANGED,
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
        await update_counters(hass)

    # trigger automations