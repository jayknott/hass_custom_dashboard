"""Event listeners and handlers used in this integration."""
from homeassistant.const import ATTR_AREA_ID, CONF_ENTITY_ID
from homeassistant.components.automation import EVENT_AUTOMATION_RELOADED
from homeassistant.core import Event
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED

from .components.automation import update_automations
from .components.counters import update_counters
from .components.registry import (
    add_entity_to_registry,
    remove_entity_from_registry,
    update_area_registry,
    update_entity_from_registry,
    update_entity_registry,
)
from .components.template import (
    update_template_areas_global,
    update_template_entities_global,
)
from .const import (
    BUILT_IN_AUTOMATION_AREA_CHANGED,
    BUILT_IN_AUTOMATION_ENTITY_CHANGED,
    BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT,
    BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT,
    CONF_ACTION,
    CONF_CREATE,
    CONF_REMOVE,
    CONF_UPDATE,
    EVENT_AREA_SETTINGS_CHANGED,
    EVENT_ENTITY_SETTINGS_CHANGED,
)
from .settings import remove_area_from_entities, remove_area_settings
from .share import get_base


async def setup_events() -> None:
    """Setup event listeners and handlers."""

    listen = get_base().hass.bus.async_listen

    listen(EVENT_AUTOMATION_RELOADED, handle_automation_reloaded)
    listen(EVENT_AREA_REGISTRY_UPDATED, handle_area_registry_updated)
    listen(EVENT_AREA_SETTINGS_CHANGED, handle_area_registry_updated)
    listen(EVENT_ENTITY_REGISTRY_UPDATED, handle_entity_registry_updated)
    listen(EVENT_ENTITY_SETTINGS_CHANGED, handle_entity_registry_updated)


async def handle_automation_reloaded(_event: Event):
    await update_automations(True)


async def handle_area_registry_updated(event: Event) -> None:
    """Handle when an area is updated."""

    base = get_base()
    create_task = base.hass.async_create_task

    await update_area_registry()
    await update_template_areas_global()

    action: str = event.data.get(CONF_ACTION)

    if action in [CONF_REMOVE]:
        await remove_area_settings(event.data[ATTR_AREA_ID])
        await remove_area_from_entities(event.data[ATTR_AREA_ID])

    if action in [CONF_CREATE, CONF_REMOVE]:
        await update_entity_registry()
        await update_template_entities_global()
        await update_counters()

    built_in = base.built_in_entities
    create_task(built_in[BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT].async_trigger({}))
    create_task(built_in[BUILT_IN_AUTOMATION_AREA_CHANGED].async_trigger({}))
    create_task(built_in[BUILT_IN_AUTOMATION_ENTITY_CHANGED].async_trigger({}))


async def handle_entity_registry_updated(event: Event) -> None:
    """Handle when an entity is updated."""

    base = get_base()
    create_task = base.hass.async_create_task

    action: str = event.data.get(CONF_ACTION)

    if action in [CONF_CREATE]:
        await add_entity_to_registry(event.data.get(CONF_ENTITY_ID))

    if action in [CONF_REMOVE]:
        await remove_entity_from_registry(event.data.get(CONF_ENTITY_ID))

    if action in [CONF_UPDATE]:
        await update_entity_from_registry(event.data.get(CONF_ENTITY_ID))

    await update_template_entities_global()

    built_in = base.built_in_entities
    create_task(built_in[BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT].async_trigger({}))
    create_task(built_in[BUILT_IN_AUTOMATION_ENTITY_CHANGED].async_trigger({}))
