"""Event listeners and handlers used in this integration."""
from homeassistant.components.automation import EVENT_AUTOMATION_RELOADED
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED

from .components.automation import update_automations
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

from .share import get_base


async def setup_events() -> None:
    """Setup event listeners and handlers."""

    listen = get_base().hass.bus.async_listen

    async def handle_automation_reloaded(_event: Event):
        await update_automations(True)

    async def handle_registry_updated(event: Event):
        await update_area_registry()
        await update_template_areas_global()
        await update_entity_registry()
        await update_template_entities_global()

    async def handle_area_registry_updated(event: Event):
        await handle_update_area(event)

    listen(EVENT_SETTINGS_CHANGED, handle_registry_updated)
    listen(EVENT_AUTOMATION_RELOADED, handle_automation_reloaded)
    listen(EVENT_AREA_REGISTRY_UPDATED, handle_area_registry_updated)
    listen(EVENT_DEVICE_REGISTRY_UPDATED, handle_registry_updated)
    listen(EVENT_ENTITY_REGISTRY_UPDATED, handle_registry_updated)


async def handle_update_area(event: Event) -> None:
    """Handle when an area is updated."""

    get_base().log.warning(f"handle_update_area event::: {event}")
    await update_area_registry()
    await update_template_areas_global()

    action: str = event.data.get(CONF_ACTION)

    if action in [CONF_REMOVE]:
        pass
        # Remove area settings
        # Remove area id from entities settings

    if action in [CONF_REMOVE, CONF_UPDATE]:
        await update_entity_registry()
        await update_template_entities_global()

    if action in [CONF_CREATE, CONF_REMOVE]:
        await update_counters()

    # trigger automations