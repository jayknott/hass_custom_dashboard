"""Add counters for entities"""
import logging
import re
from typing import Dict, List, Optional, TypedDict, Union

from homeassistant.components.template.binary_sensor import CONF_ATTRIBUTE_TEMPLATES
from homeassistant.const import (
    ATTR_ID,
    ATTR_AREA_ID,
    CONF_ENTITY_ID,
    CONF_FRIENDLY_NAME,
    CONF_ICON_TEMPLATE,
    CONF_TYPE,
    CONF_VALUE_TEMPLATE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import EntityPlatform
from homeassistant.helpers.template import Template

from .binary_sensor import create_binary_sensor_entity
from .registry import AreaSettings, EntitySettings, hass_areas
from ..const import (
    CONF_COUNT,
    CONF_COUNTERS,
    CONF_ENTITIES,
    CONF_ENTITY_PLATFORM,
    CONF_SECURITY,
    CONF_SOMETHING_ON,
    CONF_TRACKED_ENTITY_COUNT,
    CONF_VISIBLE,
    DOMAIN,
    PLATFORM_BINARY_SENSOR,
    SECURITY_ENTITY_TYPE_OFF_STATES,
    SECURITY_ENTITY_TYPES,
    SOMETHING_ON_ENTITY_TYPES,
    TITLE,
    TRACKED_ENTITY_TYPE_ON_STATES,
    TRACKED_ENTITY_TYPES,
)

PLATFORM = PLATFORM_BINARY_SENSOR
_LOGGER = logging.getLogger(__name__)


class CounterTemplates(TypedDict):
    state_template: str
    count_template: str
    entity_template: str
    tracked_count_template: str


async def setup_counters(hass: HomeAssistant) -> None:
    """Setup counters."""

    await update_counters(hass)


async def update_counters(hass: HomeAssistant) -> None:
    """Update all counters. Only creates counters when entities exist that match the counter."""

    hass.data[DOMAIN][CONF_COUNTERS] = []

    areas = await hass_areas(hass)

    # Create counters for all tracked types and something on types in every area
    for entity_type in TRACKED_ENTITY_TYPES + SOMETHING_ON_ENTITY_TYPES:
        states = [STATE_ON] + TRACKED_ENTITY_TYPE_ON_STATES.get(entity_type, [])
        for area in areas:
            await create_counter(hass, entity_type, states, None, area)

    # Create a security counter in each security type in every area
    for entity_type in SECURITY_ENTITY_TYPES:
        states = [STATE_OFF] + SECURITY_ENTITY_TYPE_OFF_STATES.get(entity_type, [])
        for area in areas:
            await create_counter(hass, entity_type, states, CONF_SECURITY, area, True)

    # Create super counters in each area for all security type and all something on types.
    for area in areas:
        await create_super_counter(
            hass, CONF_SECURITY, SECURITY_ENTITY_TYPES, CONF_SECURITY, area
        )
        await create_super_counter(
            hass, CONF_SOMETHING_ON, SOMETHING_ON_ENTITY_TYPES, None, area
        )

    # Create super counters for each tracked type
    for entity_type in TRACKED_ENTITY_TYPES:
        await create_super_counter(hass, entity_type, [entity_type])

    # Create super counter for something on types
    await create_super_counter(hass, CONF_SOMETHING_ON, SOMETHING_ON_ENTITY_TYPES)

    # Create super counter for security types
    await create_super_counter(
        hass, CONF_SECURITY, SECURITY_ENTITY_TYPES, CONF_SECURITY
    )


async def create_counter(
    hass: HomeAssistant,
    entity_type: str,
    states: List[str],
    category: Optional[str] = None,
    area: Optional[AreaSettings] = None,
    reject: bool = False,
) -> None:
    """Create a counter for a single entity type."""

    prefix = _prefix_from_category(category)
    full_entity_type = f"{prefix}{entity_type}"
    counter = await _create_counter(
        hass,
        full_entity_type,
        [full_entity_type],
        states=states,
        prefix=prefix,
        area=area,
        reject=reject,
    )

    if counter is not None:
        hass.data[DOMAIN][CONF_COUNTERS].append(counter)


async def create_super_counter(
    hass: HomeAssistant,
    name: str,
    entity_types: List[str],
    category: Optional[str] = None,
    area: Optional[AreaSettings] = None,
) -> None:
    """Create a counter based on other counters."""

    prefix = _prefix_from_category(category)
    await _create_counter(hass, name, entity_types, prefix=prefix, area=area, sum=True)


async def remove_counter(hass: HomeAssistant, entity_id: str) -> None:
    """Remove a counter from HA if it exists."""

    platform: EntityPlatform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    sensor = hass.states.get(entity_id)

    # if sensor is not None and not sensor.attributes.get("restored", False):
    if sensor is not None:
        await platform.async_remove_entity(entity_id)


def _counter_entities(
    hass: HomeAssistant, entity_type: str, area: Optional[AreaSettings] = None
) -> List[str]:
    """Enumerate the entities the counter will check for updates on."""

    entities: List[EntitySettings] = hass.data[DOMAIN][CONF_ENTITIES]
    return [
        entity[CONF_ENTITY_ID]
        for entity in entities
        if (
            entity[CONF_TYPE] == entity_type
            and entity[CONF_VISIBLE]
            and (
                (entity[ATTR_AREA_ID] == area[ATTR_ID])
                if area is not None
                else (entity[ATTR_AREA_ID] is not None)
            )
        )
    ]


def _counter_templates(
    hass: HomeAssistant,
    entity_type: str,
    states: List[str],
    area: Optional[AreaSettings] = None,
    reject: bool = False,
) -> Optional[CounterTemplates]:
    """Create the templates for the counter entity"""

    entity_ids = _counter_entities(hass, entity_type, area)

    if len(entity_ids) == 0:
        return None

    state_template = []
    count_template = []
    entity_template = []

    for id in entity_ids:
        state_template.append(f"states('{id}') {'not ' if reject else ''}in {states}")
        count_template.append(
            f"(1 if states('{id}') {'not ' if reject else ''}in {states} else 0)"
        )
        entity_template.append(
            f"('{id}' if states('{id}') {'not ' if reject else ''}in {states} else '')"
        )

    return {
        "state_template": f"{{{{ {' or '.join(state_template)} }}}}",
        "count_template": f"{{{{ {' + '.join(count_template)} }}}}",
        "entity_template": f"{{{{ [{', '.join(entity_template)}] | select('!=', '') | list }}}}",
        "tracked_count_template": f"{{{{ {len(entity_ids)} }}}}",
    }


# async def create_counter(
#     hass: HomeAssistant,
#     entity_type: str,
#     states: List[str],
#     prefix: Optional[str] = None,
#     area: Optional[AreaSettings] = None,
#     reject: bool = False,
# ) -> Optional[str]:
#     """Create a counter for a single entity type."""

#     platform: EntityPlatform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]

#     # Generate names
#     area_string = f"area_{area[ATTR_ID]}_" if area is not None else ""
#     area_title = f"Area {area[ATTR_ID][-5:-1]} " if area is not None else ""

#     prefix_title = f"{prefix.replace('_', ' ').title()} " if prefix is not None else ""
#     entity_type_title = entity_type.replace("_", " ").title()
#     full_entity_type = f"{prefix_string}{entity_type}"

#     device_id = f"{DOMAIN}_{area_string}{full_entity_type}"
#     entity_id = f"{PLATFORM}.{device_id}"
#     friendly_name = f"{TITLE} {area_title}{prefix_title}{entity_type_title}"

#     await remove_counter(hass, entity_id)
#     templates = counter_templates(hass, full_entity_type, states, area, reject)

#     if templates is None:
#         return None

#     await platform.async_add_entities(
#         [
#             await create_binary_sensor_entity(
#                 hass,
#                 device_id,
#                 {
#                     CONF_FRIENDLY_NAME: friendly_name,
#                     CONF_ICON_TEMPLATE: Template("mdi:counter"),
#                     CONF_VALUE_TEMPLATE: Template(templates["state_template"]),
#                     CONF_ATTRIBUTE_TEMPLATES: {
#                         CONF_COUNT: Template(templates["count_template"]),
#                         CONF_ENTITIES: Template(templates["entities_template"]),
#                         CONF_TRACKED_ENTITY_COUNT: Template(
#                             templates["tracked_count_template"]
#                         ),
#                     },
#                 },
#             )
#         ]
#     )

#     return entity_id


def _super_counter_entities(hass: HomeAssistant, regex: str) -> List[str]:
    """Enumerate the counters that this super counter will check for updates on."""

    entity_ids: List[str] = hass.data[DOMAIN][CONF_COUNTERS]

    return [
        entity_id for entity_id in entity_ids if re.search(regex, entity_id) is not None
    ]


def _super_counter_templates(
    hass: HomeAssistant,
    entity_types: List[str],
    area: Optional[AreaSettings] = None,
    prefix: Optional[str] = None,
) -> Optional[CounterTemplates]:
    """Create the templates for the super counter entity."""

    area_regex = f"area_{area[ATTR_ID]}_" if area is not None else "area_[a-z\\d]+_"
    regex = f"binary_sensor\\.{DOMAIN}_{area_regex}{prefix}({'|'.join(entity_types)})"

    entity_ids = _super_counter_entities(hass, regex)

    if len(entity_ids) == 0:
        return None

    state_template = []
    count_template = []
    entity_template = []
    tracked_count_template = []

    for id in entity_ids:
        state_template.append(f"is_state('{id}', '{STATE_ON}')")
        count_template.append(f"(state_attr('{id}', '{CONF_COUNT}'))")
        entity_template.append(f"(state_attr('{id}', '{CONF_ENTITIES}'))")
        tracked_count_template.append(
            f"(state_attr('{id}', '{CONF_TRACKED_ENTITY_COUNT}'))"
        )

    return {
        "state_template": f"{{{{ {' or '.join(state_template)} }}}}",
        "count_template": f"{{{{ {' + '.join(count_template)} }}}}",
        "entity_template": f"{{{{ {' + '.join(entity_template)} }}}}",
        "tracked_count_template": f"{{{{ {' + '.join(tracked_count_template)} }}}}",
    }


# async def create_super_counter(
#     hass: HomeAssistant,
#     entity_types: List[str],
#     name: str,
#     prefix: Optional[str] = None,
#     area: Optional[AreaSettings] = None,
# ) -> None:
#     """Create a counter based on other counters."""

#     platform: EntityPlatform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]

#     # Generate names
#     area_string = f"area_{area[ATTR_ID]}_" if area is not None else ""
#     area_title = f"Area {area[ATTR_ID][-5:-1]} " if area is not None else ""
#     prefix_string = f"{prefix}_" if prefix is not None else ""
#     name_title = name.replace("_", " ").title()

#     device_id = f"{DOMAIN}_{area_string}{name}"
#     entity_id = f"{PLATFORM}.{device_id}"
#     friendly_name = f"{TITLE} {area_title}{name_title}"

#     await remove_counter(hass, entity_id)

#     area_regex = f"area_{area[ATTR_ID]}_" if area is not None else "area_[a-z\\d]+_"
#     regex = f"binary_sensor\\.{DOMAIN}_{area_regex}{prefix_string}({'|'.join(entity_types)})"

#     templates = super_counter_templates(hass, regex)

#     if templates is None:
#         return

#     await platform.async_add_entities(
#         [
#             await create_binary_sensor_entity(
#                 hass,
#                 device_id,
#                 {
#                     CONF_FRIENDLY_NAME: friendly_name,
#                     CONF_ICON_TEMPLATE: Template("mdi:counter"),
#                     CONF_VALUE_TEMPLATE: Template(templates["state_template"]),
#                     CONF_ATTRIBUTE_TEMPLATES: {
#                         CONF_COUNT: Template(templates["count_template"]),
#                         CONF_ENTITIES: Template(templates["entities_template"]),
#                         CONF_TRACKED_ENTITY_COUNT: Template(
#                             templates["tracked_count_template"]
#                         ),
#                     },
#                 },
#             )
#         ]
#     )


def _prefix_from_category(category: Optional[str] = None) -> str:
    """Get the prefix for a category. Used in _create_counter."""

    return f"{category}_" if category is not None and category != "" else ""


async def _create_counter(
    hass: HomeAssistant,
    name: str,
    entity_types: Union[str, List[str]],
    states: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    area: Optional[AreaSettings] = None,
    reject: bool = False,
    sum: bool = False,
) -> Optional[str]:
    platform: EntityPlatform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]

    area_string = f"area_{area[ATTR_ID]}_" if area is not None else ""
    area_title = f"Area {area[ATTR_ID][-5:-1]} " if area is not None else ""

    device_id = f"{DOMAIN}_{area_string}{name}"
    entity_id = f"{PLATFORM}.{device_id}"
    friendly_name = f"{TITLE} {area_title}{name.replace('_', ' ').title()}"

    await remove_counter(hass, entity_id)

    templates: CounterTemplates
    if sum:
        templates = _super_counter_templates(hass, entity_types, area, prefix)
    else:
        templates = _counter_templates(hass, entity_types[0], states, area, reject)

    if templates is None:
        return None

    await platform.async_add_entities(
        [
            await create_binary_sensor_entity(
                hass,
                device_id,
                {
                    CONF_FRIENDLY_NAME: friendly_name,
                    CONF_ICON_TEMPLATE: Template("mdi:counter"),
                    CONF_VALUE_TEMPLATE: Template(templates["state_template"]),
                    CONF_ATTRIBUTE_TEMPLATES: {
                        CONF_COUNT: Template(templates["count_template"]),
                        CONF_ENTITIES: Template(templates["entity_template"]),
                        CONF_TRACKED_ENTITY_COUNT: Template(
                            templates["tracked_count_template"]
                        ),
                    },
                },
            )
        ]
    )

    return entity_id