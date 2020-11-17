from homeassistant.helpers.entity_platform import EntityPlatform
from homeassistant.core import HomeAssistant
import logging
import re

# from homeassistant.components.group import Group
from homeassistant.components.template.binary_sensor import CONF_ATTRIBUTE_TEMPLATES
from homeassistant.const import (
    ATTR_ID,
    ATTR_AREA_ID,
    ATTR_NAME,
    CONF_ENTITY_ID,
    CONF_FRIENDLY_NAME,
    CONF_ICON_TEMPLATE,
    CONF_TYPE,
    CONF_VALUE_TEMPLATE,
    CONF_STATE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.template import Template

from .binary_sensor import create_binary_sensor_entity
from .registry import hass_areas
from .const import (
    CONF_COUNT,
    CONF_ENTITIES,
    CONF_ENTITY_PLATFORM,
    CONF_SECURITY,
    CONF_SOMETHING_ON,
    CONF_TRACKED_ENTITY_COUNT,
    CONF_VISIBLE,
    DOMAIN,
    JINJA_VARIABLE_ENTITIES,
    PLATFORM_BINARY_SENSOR,
    SECURITY_ENTITY_TYPE_OFF_STATES,
    SECURITY_ENTITY_TYPES,
    SOMETHING_ON_ENTITY_TYPES,
    TITLE,
    TRACKED_ENTITY_TYPE_ON_STATES,
    TRACKED_ENTITY_TYPES,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM = PLATFORM_BINARY_SENSOR


async def update_built_in_counters(hass: HomeAssistant):
    areas = await hass_areas(hass)

    async def create_counter(entity_type, states, prefix=None, area=None, reject=False):
        platform: EntityPlatform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
        area_string = f"area_{area[ATTR_ID]}_" if area is not None else ""
        area_title = f"Area {area[ATTR_ID][-5:-1]} " if area is not None else ""
        prefix_string = f"{prefix}_" if prefix is not None else ""
        prefix_title = (
            f"{prefix.replace('_', ' ').title()} " if prefix is not None else ""
        )
        entity_type_title = entity_type.replace("_", " ").title()

        device_id = f"{DOMAIN}_{area_string}{prefix_string}{entity_type}"
        entity_id = f"{PLATFORM}.{device_id}"

        sensor = hass.states.get(entity_id)
        if sensor is not None and not sensor.attributes.get("restored", False):
            await platform.async_remove_entity(entity_id)

        # select_area = ""
        # if area is not None:
        #     select_area = f", 'equalto', '{area[ATTR_ID]}'"

        # state_filter = "selectattr" if not reject else "rejectattr"

        # Enter the entities seperately so the template listener will update faster
        entity_ids = [
            entity[CONF_ENTITY_ID]
            for entity in hass.data[DOMAIN][CONF_ENTITIES]
            if (
                entity[CONF_TYPE] == f"{prefix_string}{entity_type}"
                and entity[CONF_VISIBLE]
                and (
                    (entity[ATTR_AREA_ID] == area[ATTR_ID])
                    if area is not None
                    else (entity[ATTR_AREA_ID] is not None)
                )
            )
        ]

        if len(entity_ids) == 0:
            # _LOGGER.error(f"No entities for {entity_type} {states}")
            return None

        state_template = []
        count_template = []
        entity_template = []
        for id in entity_ids:
            state_template.append(
                f"states('{id}') {'not ' if reject else ''}in {states}"
            )
            count_template.append(
                f"(1 if states('{id}') {'not ' if reject else ''}in {states} else 0)"
            )
            entity_template.append(
                f"('{id}' if states('{id}') {'not ' if reject else ''}in {states} else '')"
            )

        # template = f"""
        #     states |
        #     selectattr('{CONF_ENTITY_ID}', 'in',
        #         {available_entities_template}
        #     ) |
        #     {state_filter}('{CONF_STATE}', 'in', {states}) |
        #     map(attribute='{CONF_ENTITY_ID}') |
        #     list
        # """

        await platform.async_add_entities(
            [
                await create_binary_sensor_entity(
                    hass,
                    device_id,
                    {
                        CONF_FRIENDLY_NAME: f"{TITLE} {area_title}{prefix_title}{entity_type_title}",
                        CONF_ICON_TEMPLATE: Template("mdi:counter"),
                        CONF_VALUE_TEMPLATE: Template(
                            f"{{{{ {' or '.join(state_template)} }}}}"
                        ),
                        CONF_ATTRIBUTE_TEMPLATES: {
                            CONF_COUNT: Template(
                                f"{{{{ {' + '.join(count_template)} }}}}"
                            ),
                            # CONF_COUNT: Template(f"{{{{ 0 }}}}"),
                            # CONF_ENTITIES: Template(f"{{{{ {template} }}}}"),
                            CONF_ENTITIES: Template(
                                f"{{{{ [{', '.join(entity_template)}] | select('!=', '') | list }}}}"
                            ),
                            CONF_TRACKED_ENTITY_COUNT: Template(
                                f"{{{{ {len(entity_ids)} }}}}"
                            ),
                            # CONF_TRACKED_ENTITY_COUNT: Template(f"{{{{ 0 }}}}"),
                        },
                    },
                )
            ]
        )

        return entity_id

    async def create_super_counter(
        existing_counters, entity_types, name, prefix=None, area=None
    ):
        platform: EntityPlatform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
        area_string = f"area_{area[ATTR_ID]}_" if area is not None else ""
        area_title = f"Area {area[ATTR_ID][-5:-1]} " if area is not None else ""
        prefix_string = f"{prefix}_" if prefix is not None else ""
        name_title = name.replace("_", " ").title()

        device_id = f"{DOMAIN}_{area_string}{name}"
        entity_id = f"{PLATFORM}.{device_id}"

        sensor = hass.states.get(entity_id)
        if sensor is not None and not sensor.attributes.get("restored", False):
            # try:
            await platform.async_remove_entity(entity_id)
            # except:
            # pass

        area_regex = f"area_{area[ATTR_ID]}_" if area is not None else "area_[a-z\\d]+_"
        regex = f"binary_sensor\\.{DOMAIN}_{area_regex}{prefix_string}({'|'.join(entity_types)})"

        entity_ids = [
            entity_id
            for entity_id in existing_counters
            if re.search(regex, entity_id) is not None
        ]

        if len(entity_ids) == 0:
            _LOGGER.warn(f"no entities for super {area_title} {name_title}")
            return

        state_entities = [
            f"is_state('{entity_id}', '{STATE_ON}')" for entity_id in entity_ids
        ]

        available_entities_template = f"""
            states |
            selectattr('{CONF_ENTITY_ID}', 'in', {entity_ids}) |
            list
        """

        # template = f"""
        #     {available_entities_template} |
        #     selectattr('{CONF_STATE}', 'equalto', '{STATE_ON}') |
        #     list
        # """

        await platform.async_add_entities(
            [
                await create_binary_sensor_entity(
                    hass,
                    device_id,
                    {
                        CONF_FRIENDLY_NAME: f"{TITLE} {area_title}{name_title}",
                        CONF_ICON_TEMPLATE: Template("mdi:counter"),
                        CONF_VALUE_TEMPLATE: Template(
                            f"{{{{ {' or '.join(state_entities)} }}}}"
                        ),
                        CONF_ATTRIBUTE_TEMPLATES: {
                            CONF_COUNT: Template(
                                f"{{{{ {available_entities_template} | sum(attribute='attributes.{CONF_COUNT}') }}}}"
                            ),
                            # CONF_COUNT: Template(f"{{{{ 0 }}}}"),
                            # CONF_ENTITIES: Template(
                            #     f"""
                            #     {{% set ns = namespace(entities=[]) %}}
                            #     {{% for entities in {template} | map(attribute='attributes.{CONF_ENTITIES}') | list %}}
                            #         {{% set ns.entities = ns.entities + entities %}}
                            #     {{% endfor %}}
                            #     {{{{ ns.entities }}}}
                            # """
                            # ),
                            CONF_ENTITIES: Template(f"{{{{ [] }}}}"),
                            CONF_TRACKED_ENTITY_COUNT: Template(
                                f"{{{{ {available_entities_template} | sum(attribute='attributes.{CONF_TRACKED_ENTITY_COUNT}') }}}}"
                            ),
                            # CONF_TRACKED_ENTITY_COUNT: Template(f"{{{{ 0 }}}}"),
                        },
                    },
                )
            ]
        )

    counters = []

    for entity_type in TRACKED_ENTITY_TYPES + SOMETHING_ON_ENTITY_TYPES:
        states = [STATE_ON] + TRACKED_ENTITY_TYPE_ON_STATES.get(entity_type, [])
        # create_task(create_counter(entity_type, states))
        for area in areas:
            counters.append(await create_counter(entity_type, states, None, area))

    for entity_type in SECURITY_ENTITY_TYPES:
        states = [STATE_OFF] + SECURITY_ENTITY_TYPE_OFF_STATES.get(entity_type, [])
        # create_task(create_counter(entity_type, states, CONF_SECURITY, None, True))
        for area in areas:
            counters.append(
                await create_counter(entity_type, states, CONF_SECURITY, area, True)
            )

    counters = [counter for counter in counters if counter is not None]

    for area in areas:
        # for entity_type in TRACKED_ENTITY_TYPES:
        # create_task(create_super_counter([entity_type], entity_type, None, area))

        await create_super_counter(
            counters, SECURITY_ENTITY_TYPES, CONF_SECURITY, CONF_SECURITY, area
        )
        await create_super_counter(
            counters, SOMETHING_ON_ENTITY_TYPES, CONF_SOMETHING_ON, None, area
        )

    for entity_type in TRACKED_ENTITY_TYPES:
        await create_super_counter(counters, [entity_type], entity_type)

    await create_super_counter(counters, SOMETHING_ON_ENTITY_TYPES, CONF_SOMETHING_ON)
    await create_super_counter(
        counters, SECURITY_ENTITY_TYPES, CONF_SECURITY, CONF_SECURITY
    )
