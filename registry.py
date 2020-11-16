from homeassistant.core import HomeAssistant
import logging
import re

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
from homeassistant.helpers.storage import Store

from .const import (
    BINARY_SENSOR_CLASS_MAP,
    CONF_AREAS,
    CONF_ENTITIES,
    CONF_ORIGINAL_AREA_ID,
    CONF_ORIGINAL_NAME,
    CONF_ORIGINAL_TYPE,
    CONF_SORT_ORDER,
    CONF_VISIBLE,
    COVER_CLASS_MAP,
    DEFAULT_ROOM_ICON,
    DEFAULT_SORT_ORDER,
    DOMAIN,
    PLATFORM_BINARY_SENSOR,
    PLATFORM_MAP,
    SENSOR_CLASS_MAP,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM = PLATFORM_BINARY_SENSOR


async def setup_registries(hass: HomeAssistant):
    hass.data[DOMAIN][CONF_AREAS] = []
    hass.data[DOMAIN][CONF_ENTITIES] = []


async def update_registries(hass: HomeAssistant):
    await update_area_registry(hass)
    await update_entity_registry(hass)


async def update_area_registry(hass: HomeAssistant):
    hass.data[DOMAIN][CONF_AREAS] = await hass_areas(hass)


async def update_entity_registry(hass: HomeAssistant):
    hass.data[DOMAIN][CONF_ENTITIES] = await hass_entities(hass)


async def hass_areas(hass):
    areas = []  # make as an array so it can be sorted

    store = Store(hass, 1, f"{DOMAIN}.{CONF_AREAS}")
    data = await store.async_load()
    if data is None:
        data = {}

    # Sorted by original name because this is what is needed for the picker
    areas_sorted = sorted(
        hass.data["area_registry"].async_list_areas(), key=lambda entry: entry.name
    )

    for area in areas_sorted:
        area_data = data.get(area.id, {})
        areas.append(
            {
                ATTR_ID: area.id,
                ATTR_NAME: area_data.get(CONF_NAME, area.name),
                CONF_ICON: area_data.get(CONF_ICON, DEFAULT_ROOM_ICON),
                CONF_ORIGINAL_NAME: area.name,
                CONF_SORT_ORDER: area_data.get(CONF_SORT_ORDER, DEFAULT_SORT_ORDER),
                CONF_VISIBLE: area_data.get(CONF_VISIBLE, True),
            }
        )

    return areas


def original_entity_type(hass, entity_id):
    entity = hass.states.get(entity_id)
    domain = entity.domain if entity is not None else entity_id.split(".")[0]

    def binary_sensors():
        return BINARY_SENSOR_CLASS_MAP.get(
            entity.attributes.get("device_class"),
            BINARY_SENSOR_CLASS_MAP.get(CONF_DEFAULT, domain),
        )

    def covers():
        return COVER_CLASS_MAP.get(
            entity.attributes.get("device_class"),
            COVER_CLASS_MAP.get(CONF_DEFAULT, domain),
        )

    def sensors():
        return SENSOR_CLASS_MAP.get(
            entity.attributes.get("device_class"),
            SENSOR_CLASS_MAP.get(CONF_DEFAULT, domain),
        )

    def other():
        return PLATFORM_MAP.get(domain, PLATFORM_MAP.get(CONF_DEFAULT, domain))

    switcher = {
        "binary_sensor": binary_sensors,
        "cover": covers,
        "sensor": sensors,
    }

    if entity is None:
        return other()

    return switcher.get(domain, other)()


def match_area_with_entity_id(entity_id, areas):
    if entity_id is None or areas is None:
        return None

    for area in areas:
        name = area.name.lower().replace(" ", "_")
        quote = "'"
        regex = f"(all_)?({name.replace(quote, '')}|{name.replace(quote, '_')})_"
        if re.match(regex, entity_id.split(".")[-1]):
            return area.id

    return None


async def hass_entities(hass):
    entities = []  # make as an array so it can be sorted
    entities_processed = []  # keep track of ids so they don't get processed twice

    store = Store(hass, 1, f"{DOMAIN}.{CONF_ENTITIES}")
    data = await store.async_load()
    if data is None:
        data = {}

    areas = hass.data["area_registry"].async_list_areas()

    for area in areas:
        for device in hass.helpers.device_registry.async_entries_for_area(
            hass.data["device_registry"], area.id
        ):
            for entity in hass.helpers.entity_registry.async_entries_for_device(
                hass.data["entity_registry"], device.id
            ):
                entity_data = data.get(entity.entity_id, {})
                entity_state = hass.states.get(entity.entity_id)
                entity_name = entity_state.name if entity_state is not None else None
                entity_type = original_entity_type(hass, entity.entity_id)
                if entity_name is None:
                    entity_name = (
                        entity.name
                        if entity.name is not None
                        else entity.entity_id.split(".")[-1]
                    )
                entities.append(
                    {
                        CONF_ENTITY_ID: entity.entity_id,
                        ATTR_AREA_ID: entity_data.get(ATTR_AREA_ID, area.id),
                        CONF_ORIGINAL_AREA_ID: area.id,
                        ATTR_NAME: entity_name,
                        CONF_TYPE: entity_data.get(CONF_TYPE, entity_type),
                        CONF_ORIGINAL_TYPE: entity_type,
                        CONF_SORT_ORDER: entity_data.get(
                            CONF_SORT_ORDER, DEFAULT_SORT_ORDER
                        ),
                        CONF_VISIBLE: entity_data.get(CONF_VISIBLE, True),
                    }
                )
                entities_processed.append(entity.entity_id)

    for entity_id in hass.states.async_entity_ids():
        if entity_id in entities_processed:
            continue

        entity_data = data.get(entity_id, {})
        hass_state = hass.states.get(entity_id)
        entity_type = original_entity_type(hass, entity_id)
        area_id = entity_data.get(
            ATTR_AREA_ID, match_area_with_entity_id(entity_id, areas)
        )

        entities.append(
            {
                CONF_ENTITY_ID: entity_id,
                ATTR_AREA_ID: area_id,
                CONF_ORIGINAL_AREA_ID: None,
                ATTR_NAME: hass_state.name,
                CONF_TYPE: entity_data.get(CONF_TYPE, entity_type),
                CONF_ORIGINAL_TYPE: entity_type,
                CONF_SORT_ORDER: entity_data.get(CONF_SORT_ORDER, DEFAULT_SORT_ORDER),
                CONF_VISIBLE: entity_data.get(CONF_VISIBLE, True),
            }
        )

    return sorted(entities, key=lambda entity: entity[ATTR_NAME])
