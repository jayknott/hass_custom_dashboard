import logging

from homeassistant.components.template.binary_sensor import (
    CONF_ATTRIBUTE_TEMPLATES,
    _async_create_entities,
)
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_FRIENDLY_NAME,
    CONF_SENSORS,
    CONF_UNIQUE_ID,
    CONF_VALUE_TEMPLATE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.template import Template

from .const import (
    BUILT_IN_AREA_SELECT,
    # BUILT_IN_AREAS,
    BUILT_IN_AREA_SELECTED,
    # BUILT_IN_CONFIG,
    # BUILT_IN_ENTITIES,
    BUILT_IN_ENTITY_IDS,
    BUILT_IN_ENTITY_ID_SELECT,
    BUILT_IN_ENTITY_SELECTED,
    # CONF_AREAS,
    CONF_BUILT_IN_ENTITIES,
    # CONF_ENTITIES,
    CONF_ENTITY_PLATFORM,
    CONF_MISSING_RESOURCES,
    CONF_ORIGINAL_NAME,
    CONF_SELECTED_AREA,
    CONF_SELECTED_ENTITY,
    DOMAIN,
    JINJA_VARIABLE_AREAS,
    JINJA_VARIABLE_ENTITIES,
    PLATFORM_BINARY_SENSOR,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM = PLATFORM_BINARY_SENSOR


async def create_binary_sensor_entity(hass, device_id, conf={}):
    config = {
        CONF_SENSORS: {
            device_id: {
                CONF_FRIENDLY_NAME: device_id,
                CONF_VALUE_TEMPLATE: None,
                CONF_ATTRIBUTE_TEMPLATES: {},
            }
        }
    }
    config[CONF_SENSORS][device_id].update(conf)

    entity = (await _async_create_entities(hass, config))[0]
    entity.entity_id = f"{PLATFORM}.{device_id}"

    return entity


# async def update_built_in_binary_sensors(hass):
#     data = hass.data[DOMAIN]
#     built_in = data[CONF_BUILT_IN_ENTITIES]
#     platform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
#     to_add = []

# areas = await hass_areas(hass)

# Sensor to store config info, just static info so can just be created and updated.
# hass.states.async_set(
#     f"{PLATFORM}.{DOMAIN}_{BUILT_IN_CONFIG}",
#     STATE_ON if len(data[CONF_MISSING_RESOURCES]) == 0 else STATE_OFF,
#     {
#         CONF_FRIENDLY_NAME: f"{TITLE} Configuration",
#         CONF_MISSING_RESOURCES: data[CONF_MISSING_RESOURCES],
#     },
# )

# # Areas sensor, just static info so can just be created and updated.
# hass.states.async_set(
#     f"{PLATFORM}.{DOMAIN}_{BUILT_IN_AREAS}",
#     STATE_ON,
#     {CONF_FRIENDLY_NAME: f"{TITLE} Areas", CONF_AREAS: areas},
# )

# Selected area sensor, template values so needs to be added to the platform, will update automatically
# if built_in.get(BUILT_IN_AREA_SELECTED) is None:
#     built_in[BUILT_IN_AREA_SELECTED] = await create_binary_sensor_entity(
#         hass,
#         f"{DOMAIN}_{BUILT_IN_AREA_SELECTED}",
#         {
#             CONF_FRIENDLY_NAME: f"{TITLE} Selected Area",
#             CONF_VALUE_TEMPLATE: Template(STATE_ON),
#             CONF_ATTRIBUTE_TEMPLATES: {
#                 CONF_SELECTED_AREA: Template(
#                     f"""
#                         {{{{
#                             {JINJA_VARIABLE_AREAS} |
#                             selectattr('{CONF_ORIGINAL_NAME}', 'equalto', states('{BUILT_IN_ENTITY_IDS[BUILT_IN_AREA_SELECT]}')) |
#                             first
#                         }}}}
#                     """
#                 ),
#             },
#         },
#     )
#     to_add.append(built_in[BUILT_IN_AREA_SELECTED])

# # Entities sensor
# hass.states.async_set(
#     f"{PLATFORM}.{DOMAIN}_{BUILT_IN_ENTITIES}",
#     STATE_ON,
#     {
#         CONF_FRIENDLY_NAME: f"{TITLE} Entities",
#         CONF_ENTITIES: await hass_entities(hass),
#     },
# )

# Selected entity sensor, template values so needs to be added to the platform, will update automatically
# if built_in.get(BUILT_IN_ENTITY_SELECTED) is None:
#     built_in[BUILT_IN_ENTITY_SELECTED] = await create_binary_sensor_entity(
#         hass,
#         f"{DOMAIN}_{BUILT_IN_ENTITY_SELECTED}",
#         {
#             CONF_FRIENDLY_NAME: f"{TITLE} Selected Entity",
#             CONF_VALUE_TEMPLATE: Template(STATE_ON),
#             CONF_ATTRIBUTE_TEMPLATES: {
#                 CONF_SELECTED_ENTITY: Template(
#                     f"""
#                         {{{{
#                             {JINJA_VARIABLE_ENTITIES} |
#                             selectattr('{CONF_ENTITY_ID}', 'equalto', states('{BUILT_IN_ENTITY_IDS[BUILT_IN_ENTITY_ID_SELECT]}')) |
#                             first
#                         }}}}
#                     """
#                 ),
#             },
#         },
#     )
#     to_add.append(built_in[BUILT_IN_ENTITY_SELECTED])

# await platform.async_add_entities(to_add)
