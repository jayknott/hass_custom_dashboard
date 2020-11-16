import logging

# from homeassistant.components.group import Group
from homeassistant.components.template.binary_sensor import CONF_ATTRIBUTE_TEMPLATES
from homeassistant.const import (
    ATTR_ID,
    ATTR_AREA_ID,
    CONF_ENTITY_ID,
    CONF_FRIENDLY_NAME,
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


async def update_built_in_counters(hass):
    areas = await hass_areas(hass)

    async def create_counter(entity_type, states, prefix=None, area=None, reject=False):
        platform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
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
            return

        select_area = ""
        if area is not None:
            select_area = f", 'equalto', '{area[ATTR_ID]}'"

        state_filter = "selectattr" if not reject else "rejectattr"

        available_entities_template = f"""
            {JINJA_VARIABLE_ENTITIES} |
            selectattr('{CONF_TYPE}', 'equalto', '{prefix_string}{entity_type}') |
            selectattr('{CONF_VISIBLE}') |
            selectattr('{ATTR_AREA_ID}'{select_area}) |
            map(attribute='{CONF_ENTITY_ID}') |
            list
        """

        template = f"""
            states |
            selectattr('{CONF_ENTITY_ID}', 'in',
                {available_entities_template}
            ) |
            {state_filter}('{CONF_STATE}', 'in', {states}) |
            map(attribute='{CONF_ENTITY_ID}') |
            list
        """

        await platform.async_add_entities(
            [
                await create_binary_sensor_entity(
                    hass,
                    device_id,
                    {
                        CONF_FRIENDLY_NAME: f"{TITLE} {area_title}{prefix_title}{entity_type_title}",
                        CONF_VALUE_TEMPLATE: Template(
                            f"{{{{ {template} | count > 0 }}}}"
                        ),
                        CONF_ATTRIBUTE_TEMPLATES: {
                            CONF_COUNT: Template(f"{{{{ {template} | count }}}}"),
                            CONF_ENTITIES: Template(f"{{{{ {template} }}}}"),
                            CONF_TRACKED_ENTITY_COUNT: Template(
                                f"{{{{ {available_entities_template} | count }}}}"
                            ),
                        },
                    },
                )
            ]
        )

    async def create_super_counter(entity_types, name, prefix=None, area=None):
        platform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
        area_string = f"area_{area[ATTR_ID]}_" if area is not None else ""
        area_title = f"Area {area[ATTR_ID][-5:-1]} " if area is not None else ""
        prefix_string = f"{prefix}_" if prefix is not None else ""
        name_title = name.replace("_", " ").title()

        device_id = f"{DOMAIN}_{area_string}{name}"
        entity_id = f"{PLATFORM}.{device_id}"

        sensor = hass.states.get(entity_id)
        if sensor is not None and not sensor.attributes.get("restored", False):
            return

        entity_ids = [
            f"{PLATFORM}.{DOMAIN}_{area_string}{prefix_string}{entity_type}"
            for entity_type in entity_types
        ]

        available_entities_template = f"""
            states |
            selectattr('{CONF_ENTITY_ID}', 'in', {entity_ids}) |
            list
        """

        template = f"""
            {available_entities_template} |
            selectattr('{CONF_STATE}', 'equalto', '{STATE_ON}') |
            list
        """

        await platform.async_add_entities(
            [
                await create_binary_sensor_entity(
                    hass,
                    device_id,
                    {
                        CONF_FRIENDLY_NAME: f"{TITLE} {area_title}{name_title}",
                        CONF_VALUE_TEMPLATE: Template(
                            f"{{{{ {template} | count > 0 }}}}"
                        ),
                        CONF_ATTRIBUTE_TEMPLATES: {
                            CONF_COUNT: Template(
                                f"{{{{ {template} | sum(attribute='attributes.{CONF_COUNT}') }}}}"
                            ),
                            CONF_ENTITIES: Template(
                                f"""
                                {{% set ns = namespace(entities=[]) %}}
                                {{% for entities in {template} | map(attribute='attributes.{CONF_ENTITIES}') | list %}}
                                    {{% set ns.entities = ns.entities + entities %}}
                                {{% endfor %}}
                                {{{{ ns.entities }}}}
                            """
                            ),
                            CONF_TRACKED_ENTITY_COUNT: Template(
                                f"{{{{ {available_entities_template} | sum(attribute='attributes.{CONF_TRACKED_ENTITY_COUNT}') }}}}"
                            ),
                        },
                    },
                )
            ]
        )

    create_task = hass.async_create_task

    for entity_type in TRACKED_ENTITY_TYPES + SOMETHING_ON_ENTITY_TYPES:
        states = [STATE_ON] + TRACKED_ENTITY_TYPE_ON_STATES.get(entity_type, [])
        # create_task(create_counter(entity_type, states))
        for area in areas:
            create_task(create_counter(entity_type, states, None, area))

    for entity_type in SECURITY_ENTITY_TYPES:
        states = [STATE_OFF] + SECURITY_ENTITY_TYPE_OFF_STATES.get(entity_type, [])
        # create_task(create_counter(entity_type, states, CONF_SECURITY, None, True))
        for area in areas:
            create_task(create_counter(entity_type, states, CONF_SECURITY, area, True))

    for entity_type in TRACKED_ENTITY_TYPES:
        create_task(create_super_counter([entity_type], entity_type))

    create_task(create_super_counter(SOMETHING_ON_ENTITY_TYPES, CONF_SOMETHING_ON))
    create_task(
        create_super_counter(SECURITY_ENTITY_TYPES, CONF_SECURITY, CONF_SECURITY)
    )

    for area in areas:
        # for entity_type in TRACKED_ENTITY_TYPES:
        # create_task(create_super_counter([entity_type], entity_type, None, area))

        create_task(
            create_super_counter(
                SECURITY_ENTITY_TYPES, CONF_SECURITY, CONF_SECURITY, area
            )
        )
        create_task(
            create_super_counter(
                SOMETHING_ON_ENTITY_TYPES, CONF_SOMETHING_ON, None, area
            )
        )
