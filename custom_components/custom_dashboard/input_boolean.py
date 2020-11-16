import logging

from homeassistant.components.input_boolean import (
    CONF_INITIAL,
    InputBoolean,
)
from homeassistant.const import (
    CONF_ICON,
    CONF_ID,
    CONF_NAME,
    STATE_OFF,
)
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_ENTITY_PLATFORM,
    BUILT_IN_AREA_VISIBLE,
    BUILT_IN_ENTITY_VISIBLE,
    CONF_BUILT_IN_ENTITIES,
    DOMAIN,
    PLATFORM_INPUT_BOOLEAN,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM = PLATFORM_INPUT_BOOLEAN


def create_input_boolean_entity(device_id, conf={}):
    entity_id = f"{PLATFORM}.{device_id}"
    config = {
        CONF_ID: entity_id.split(".")[-1],
        CONF_NAME: entity_id.split(".")[-1],
        CONF_ICON: "mdi:checkbox-marked-outline",
        CONF_INITIAL: STATE_OFF,
    }
    config.update(conf)

    entity = CustomInputBoolean(config, True)

    return entity


async def update_built_in_input_boolean(hass):
    data = hass.data[DOMAIN]
    built_in = data[CONF_BUILT_IN_ENTITIES]
    platform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add = []

    # Area icon setting
    if built_in.get(BUILT_IN_AREA_VISIBLE) is None:
        built_in[BUILT_IN_AREA_VISIBLE] = create_input_boolean_entity(
            f"{DOMAIN}_{BUILT_IN_AREA_VISIBLE}",
            {CONF_NAME: f"{TITLE} Area Visible", CONF_ICON: "mdi:eye"},
        )
        to_add.append(built_in[BUILT_IN_AREA_VISIBLE])

    # Area icon setting
    if built_in.get(BUILT_IN_ENTITY_VISIBLE) is None:
        built_in[BUILT_IN_ENTITY_VISIBLE] = create_input_boolean_entity(
            f"{DOMAIN}_{BUILT_IN_ENTITY_VISIBLE}",
            {CONF_NAME: f"{TITLE} Entity Visible", CONF_ICON: "mdi:eye"},
        )
        to_add.append(built_in[BUILT_IN_ENTITY_VISIBLE])

    await platform.async_add_entities(to_add)


class CustomInputBoolean(InputBoolean):
    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass