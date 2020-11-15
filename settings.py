import logging
from typing import Optional
import voluptuous as vol

from homeassistant.const import (
    ATTR_AREA_ID,
    ATTR_NAME,
    CONF_ENTITY_ID,
    CONF_ICON,
    CONF_TYPE,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.storage import Store

from .const import (
    BUILT_IN_ENTITIES, BUILT_IN_ENTITY_IDS, CONF_AREA,
    CONF_AREA_NAME,
    CONF_AREAS,
    CONF_ENTITIES,
    CONF_ENTITY, CONF_ORIGINAL_AREA_ID, CONF_ORIGINAL_TYPE,
    CONF_SORT_ORDER,
    CONF_VISIBLE,
    DEFAULT_ROOM_ICON,
    DEFAULT_SORT_ORDER,
    DOMAIN,
    ENTITY_TYPES,
    EVENT_SETTINGS_CHANGED,
    PLATFORM_BINARY_SENSOR,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM = PLATFORM_BINARY_SENSOR

CONF_UPDATED = "updated"

SCHEMA_UPDATE_AREA_SERVICE = vol.Schema(
    {
        vol.Required(CONF_AREA_NAME): vol.All(str, vol.Length(min=1)),
        vol.Optional(CONF_ICON): cv.icon,
        vol.Optional(ATTR_NAME): vol.All(str, vol.Length(min=1)),
        vol.Optional(CONF_SORT_ORDER): vol.All(str, vol.Length(min=1, max=8)),
        vol.Optional(CONF_VISIBLE): cv.boolean,
    }
)

SCHEMA_UPDATE_ENTITY_SERVICE = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Optional(CONF_AREA_NAME): vol.All(str, vol.Length(min=0)),
        vol.Optional(CONF_SORT_ORDER): vol.All(str, vol.Length(min=1, max=8)),
        vol.Optional(CONF_TYPE): vol.In(ENTITY_TYPES),
        vol.Optional(CONF_VISIBLE): cv.boolean,
    }
)


async def save_setting(hass, setting_type, call):
    updated = False

    # Have to do this because it comes from the template as a string
    if CONF_SORT_ORDER in call.data:
        try:
            int(float(call.data[CONF_SORT_ORDER]))
        except:
            raise vol.error.SchemaError("Expected an integer for sort_order.")

    if setting_type == CONF_AREA:
        updated = await _update_area(hass, call) or updated

    if setting_type == CONF_ENTITY:
        updated = await _update_entity(hass, call) or updated

    if updated:
        hass.bus.fire(EVENT_SETTINGS_CHANGED)


async def _update_area(hass, call):
    store = Store(hass, 1, f"{DOMAIN}.{CONF_AREAS}")
    data = await store.async_load()
    if data is None:
        data = {}
    data[CONF_UPDATED] = False
    
    area_name = call.data.get(CONF_AREA_NAME)
    area_id = await _get_area_id_by_name(hass, area_name)

    await _update_key_value(hass, data, call, area_id, ATTR_NAME, area_name)
    await _update_key_value(hass, data, call, area_id, CONF_ICON, DEFAULT_ROOM_ICON)
    await _update_key_value(hass, data, call, area_id, CONF_SORT_ORDER, DEFAULT_SORT_ORDER)
    await _update_key_value(hass, data, call, area_id, CONF_VISIBLE, True)

    return await _store_data(store, data, area_id)


async def _update_entity(hass, call):
    store = Store(hass, 1, f"{DOMAIN}.{CONF_ENTITIES}")
    data = await store.async_load()
    if data is None:
        data = {}
    data[CONF_UPDATED] = False
    
    entity_id = call.data.get(CONF_ENTITY_ID)
    entity = _get_entity_by_id(hass, entity_id)

    await _update_key_value(hass, data, call, entity_id, CONF_AREA_NAME, entity[CONF_ORIGINAL_AREA_ID])
    await _update_key_value(hass, data, call, entity_id, CONF_SORT_ORDER, DEFAULT_SORT_ORDER)
    await _update_key_value(hass, data, call, entity_id, CONF_TYPE, [entity[CONF_ORIGINAL_TYPE], None])
    await _update_key_value(hass, data, call, entity_id, CONF_VISIBLE, True)

    return await _store_data(store, data, entity_id)


async def _get_area_id_by_name(hass, area_name):
    area = None
    if area_name is not None and area_name != '':
        areas = hass.data["area_registry"].async_list_areas()
        area = next((area_obj for area_obj in areas if area_obj.name == area_name), None)
    else:
        return None

    if area is None:
        raise vol.error.SchemaError(
            f"Cannot update area because an area with name '{area_name}' doesn't exist"
        )

    return area.id


def _get_entity_by_id(hass, entity_id):
    entity = None
    if entity_id is not None and entity_id != '':
        entities = hass.states.get(BUILT_IN_ENTITY_IDS[BUILT_IN_ENTITIES]).attributes[CONF_ENTITIES]
        entity = next((entity_obj for entity_obj in entities if entity_obj[CONF_ENTITY_ID] == entity_id), None)
    else:
        return None

    if entity is None:
        raise vol.error.SchemaError(
            f"Cannot update entity because an entity with id '{entity_id}' doesn't exist"
        )
    
    return entity


async def _store_data(store, data, object_key):
    if data[CONF_UPDATED]:
        del data[CONF_UPDATED]
        if len(data[object_key].keys()) == 0:
            del data[object_key]
    
        await store.async_save(data)
        return True
    
    return False

async def _update_key_value(hass, data, call, object_key, field_key, default_value=None, remove_if_default=True):
    if field_key not in call.data:
        return

    if object_key not in data:
        data[object_key] = {}

    new_value = call.data.get(field_key)
    if new_value == '':
      new_value = None

    if field_key == CONF_AREA_NAME:
        field_key = ATTR_AREA_ID
        area_id = await _get_area_id_by_name(hass, new_value)
        new_value = area_id

    old_value = data[object_key].get(field_key)

    # Convert integers from strings
    if field_key in [CONF_SORT_ORDER]:
        new_value = int(float(new_value))

    field_key_persisted = field_key in data[object_key]
    new_value_is_default = False
    if isinstance(default_value, list):
        new_value_is_default = new_value in default_value
    else:
        new_value_is_default = new_value == default_value

    if remove_if_default and new_value_is_default:
        if field_key_persisted:
            del data[object_key][field_key]
            data[CONF_UPDATED] = True
        return

    if new_value == old_value:
        return

    data[object_key][field_key] = new_value
    data[CONF_UPDATED] = True
