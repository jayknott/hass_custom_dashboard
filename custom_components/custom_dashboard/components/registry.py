"""Setup and manage area or entity registries."""
import re
from typing import Callable, Dict, Iterable, List, Optional

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
from homeassistant.helpers.entity_registry import RegistryEntry
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.area_registry import AreaEntry, AreaRegistry
from homeassistant.helpers.storage import Store

from ..const import (
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
from ..model import (
    AreaSettings,
    AreaSettingsRegistry,
    EntitySettings,
    EntitySettingsRegistry,
)
from ..share import get_base

PLATFORM = PLATFORM_BINARY_SENSOR


async def setup_registries() -> None:
    """Initialize the area and entity domain data entries."""

    base = get_base()
    base.areas = []
    base.entities = []


async def update_registries() -> None:
    """Update the area and entity domain data entries with new registry data."""

    await update_area_registry()
    await update_entity_registry()


async def update_area_registry() -> None:
    """Update the area domain data entry with new registry data."""

    get_base().areas = await hass_areas()


async def update_entity_registry() -> None:
    """Update the entity domain data entry with new registry data."""

    get_base().entities = await hass_entities()


async def add_entity_to_registry(entity_id: str) -> None:
    """Add an entity to the registry"""

    base = get_base()

    entities = base.entities
    entity: Optional[RegistryEntry] = base.hass.data["entity_registry"].async_get(
        entity_id
    )
    entity_type = original_entity_type(entity_id)

    if entity.disabled:
        return

    entities.append(
        {
            CONF_ENTITY_ID: entity_id,
            ATTR_AREA_ID: entity.area_id,
            CONF_ORIGINAL_AREA_ID: entity.area_id,
            ATTR_NAME: entity.name,
            CONF_TYPE: entity_type,
            CONF_ORIGINAL_TYPE: entity_type,
            CONF_SORT_ORDER: DEFAULT_SORT_ORDER,
            CONF_VISIBLE: True,
        }
    )


async def remove_entity_from_registry(entity_id: str) -> None:
    """Remove an entity from the registry"""

    base = get_base()

    entities = base.entities
    for entity in entities:
        if entity[CONF_ENTITY_ID] == entity_id:
            entities.remove(entity)
            break


async def update_entity_from_registry(entity_id: str) -> None:
    """Update an entity from the registry"""

    base = get_base()
    hass = base.hass
    store = Store(hass, 1, f"{DOMAIN}.{CONF_ENTITIES}")
    data: Optional[EntitySettingsRegistry] = await store.async_load()
    if data is None:
        data = {}

    entities = base.entities
    entity: Optional[RegistryEntry] = hass.data["entity_registry"].async_get(entity_id)

    entity_data = data.get(entity_id, {})
    entity_state = base.hass.states.get(entity_id)
    entity_name = entity_state.name if entity_state is not None else None
    entity_type = original_entity_type(entity_id)
    if entity_name is None:
        entity_name = (
            entity.name
            if entity.name is not None
            else entity.entity_id.split(".")[-1].replace("_", " ").title()
        )

    await remove_entity_from_registry(entity_id)

    entities.append(
        {
            CONF_ENTITY_ID: entity.entity_id,
            ATTR_AREA_ID: entity_data.get(ATTR_AREA_ID, entity.area_id),
            CONF_ORIGINAL_AREA_ID: entity.area_id,
            ATTR_NAME: entity_name,
            CONF_TYPE: entity_data.get(CONF_TYPE, entity_type),
            CONF_ORIGINAL_TYPE: entity_type,
            CONF_SORT_ORDER: entity_data.get(CONF_SORT_ORDER, DEFAULT_SORT_ORDER),
            CONF_VISIBLE: entity_data.get(CONF_VISIBLE, True),
        }
    )


async def hass_areas() -> List[AreaSettings]:
    """A dictionary list for the HA area registry used for this integrations domain data."""

    hass = get_base().hass

    areas: List[AreaSettings] = []  # make as an array so it can be sorted

    store = Store(hass, 1, f"{DOMAIN}.{CONF_AREAS}")
    data: Optional[AreaSettingsRegistry] = await store.async_load()
    if data is None:
        data = {}

    # Sorted by original name because this is what is needed for the picker
    area_registry: AreaRegistry = hass.data["area_registry"]
    areas_sorted: Iterable[AreaEntry] = sorted(
        area_registry.async_list_areas(), key=lambda entry: entry.name
    )

    for area in areas_sorted:
        area_data = data.get(area.id, {})
        area_item: AreaSettings = {
            ATTR_ID: area.id,
            ATTR_NAME: area_data.get(CONF_NAME, area.name),
            CONF_ICON: area_data.get(CONF_ICON, DEFAULT_ROOM_ICON),
            CONF_ORIGINAL_NAME: area.name,
            CONF_SORT_ORDER: area_data.get(CONF_SORT_ORDER, DEFAULT_SORT_ORDER),
            CONF_VISIBLE: area_data.get(CONF_VISIBLE, True),
        }
        areas.append(area_item)

    return areas


def original_entity_type(entity_id: str) -> str:
    """Entity type from defined maps in const.py or the entity domain."""

    entity = get_base().hass.states.get(entity_id)
    domain = entity.domain if entity is not None else entity_id.split(".")[0]

    def binary_sensors() -> str:
        return BINARY_SENSOR_CLASS_MAP.get(
            entity.attributes.get("device_class"),
            BINARY_SENSOR_CLASS_MAP.get(CONF_DEFAULT, domain),
        )

    def covers() -> str:
        return COVER_CLASS_MAP.get(
            entity.attributes.get("device_class"),
            COVER_CLASS_MAP.get(CONF_DEFAULT, domain),
        )

    def sensors() -> str:
        return SENSOR_CLASS_MAP.get(
            entity.attributes.get("device_class"),
            SENSOR_CLASS_MAP.get(CONF_DEFAULT, domain),
        )

    def other() -> str:
        return PLATFORM_MAP.get(domain, PLATFORM_MAP.get(CONF_DEFAULT, domain))

    switcher: Dict[str, Callable[[], str]] = {
        "binary_sensor": binary_sensors,
        "cover": covers,
        "sensor": sensors,
    }

    if entity is None:
        return other()

    return switcher.get(domain, other)()


def match_area_with_entity_id(
    entity_id: Optional[str], areas: Optional[List[AreaEntry]]
) -> Optional[str]:
    """
    Match and area with an entity by checking if the area name is at the
    beginning of the entity ID.
    """

    if entity_id is None or areas is None:
        return None

    for area in areas:
        name = area.name.lower().replace(" ", "_")
        quote = "'"
        regex = f"(all_)?({name.replace(quote, '')}|{name.replace(quote, '_')})_"
        if re.match(regex, entity_id.split(".")[-1]):
            return area.id

    return None


async def hass_entities() -> List[EntitySettings]:
    """A dictionary list for the HA entity registry used for this integrations domain data."""

    hass = get_base().hass

    entities: List[EntitySettings] = []  # make as an array so it can be sorted
    entities_processed: List[
        str
    ] = []  # keep track of ids so they don't get processed twice

    store = Store(hass, 1, f"{DOMAIN}.{CONF_ENTITIES}")
    data: Optional[EntitySettingsRegistry] = await store.async_load()
    if data is None:
        data = {}

    area_registry: AreaRegistry = hass.data["area_registry"]
    areas = area_registry.async_list_areas()

    # Iterate through the registry first.
    for area in areas:
        devices: Iterable[
            DeviceEntry
        ] = hass.helpers.device_registry.async_entries_for_area(
            hass.data["device_registry"], area.id
        )
        for device in devices:
            entity_entries: Iterable[
                RegistryEntry
            ] = hass.helpers.entity_registry.async_entries_for_device(
                hass.data["entity_registry"], device.id
            )
            for entity in entity_entries:
                if entity.disabled:
                    continue

                entity_data = data.get(entity.entity_id, {})
                entity_state = hass.states.get(entity.entity_id)
                entity_name = entity_state.name if entity_state is not None else None
                entity_type = original_entity_type(entity.entity_id)
                if entity_name is None:
                    entity_name = (
                        entity.name
                        if entity.name is not None
                        else entity.entity_id.split(".")[-1].replace("_", " ").title()
                    )
                entity_item: EntitySettings = {
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
                entities.append(entity_item)
                entities_processed.append(entity.entity_id)

    # Iterate through the state machine incase anything isn't listed in the registry.
    for entity_id in hass.states.async_entity_ids():
        if entity_id in entities_processed:
            continue

        entity_data = data.get(entity_id, {})
        hass_state = hass.states.get(entity_id)
        entity_type = original_entity_type(entity_id)
        area_id = entity_data.get(
            ATTR_AREA_ID, match_area_with_entity_id(entity_id, areas)
        )
        entity_item: EntitySettings = {
            CONF_ENTITY_ID: entity_id,
            ATTR_AREA_ID: area_id,
            CONF_ORIGINAL_AREA_ID: None,
            ATTR_NAME: hass_state.name,
            CONF_TYPE: entity_data.get(CONF_TYPE, entity_type),
            CONF_ORIGINAL_TYPE: entity_type,
            CONF_SORT_ORDER: entity_data.get(CONF_SORT_ORDER, DEFAULT_SORT_ORDER),
            CONF_VISIBLE: entity_data.get(CONF_VISIBLE, True),
        }
        entities.append(entity_item)

    return sorted(entities, key=lambda entity: entity[ATTR_NAME])
