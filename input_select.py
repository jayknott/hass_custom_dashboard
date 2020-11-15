import logging

from homeassistant.components.input_select import (
    CONF_OPTIONS,
    InputSelect,
)
from homeassistant.const import (
    CONF_ICON,
    CONF_ID,
    CONF_NAME,
)
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_ENTITY_PLATFORM,
    BUILT_IN_AREA_SELECT,
    BUILT_IN_ENTITY_AREA_SELECT,
    BUILT_IN_ENTITY_ID_SELECT,
    BUILT_IN_ENTITY_TYPE_SELECT,
    CONF_BUILT_IN_ENTITIES,
    DOMAIN,
    ENTITY_TYPES,
    PLATFORM_INPUT_SELECT,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM = PLATFORM_INPUT_SELECT


def create_input_select_entity(device_id, conf={}):
    config = {
        CONF_ID: device_id,
        CONF_NAME: device_id,
        CONF_ICON: "mdi:form-textbox",
        CONF_OPTIONS: [""],
    }
    config.update(conf)

    entity = CustomInputSelect.from_yaml(config)

    return entity


async def update_built_in_input_select(hass):
    data = hass.data[DOMAIN]
    built_in = data[CONF_BUILT_IN_ENTITIES]
    platform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add = []

    # Area select
    if built_in.get(BUILT_IN_AREA_SELECT) is None:
        built_in[BUILT_IN_AREA_SELECT] = create_input_select_entity(
            f"{DOMAIN}_{BUILT_IN_AREA_SELECT}",
            {CONF_NAME: f"{TITLE} Area", CONF_ICON: "mdi:sofa"},
        )
        to_add.append(built_in[BUILT_IN_AREA_SELECT])

    # Entity area select
    if built_in.get(BUILT_IN_ENTITY_AREA_SELECT) is None:
        built_in[BUILT_IN_ENTITY_AREA_SELECT] = create_input_select_entity(
            f"{DOMAIN}_{BUILT_IN_ENTITY_AREA_SELECT}",
            {CONF_NAME: f"{TITLE} Entity Area", CONF_ICON: "mdi:sofa"},
        )
        to_add.append(built_in[BUILT_IN_ENTITY_AREA_SELECT])

    # Entity id select
    if built_in.get(BUILT_IN_ENTITY_ID_SELECT) is None:
        built_in[BUILT_IN_ENTITY_ID_SELECT] = create_input_select_entity(
            f"{DOMAIN}_{BUILT_IN_ENTITY_ID_SELECT}",
            {CONF_NAME: f"{TITLE} Entity ID", CONF_ICON: "mdi:devices"},
        )
        to_add.append(built_in[BUILT_IN_ENTITY_ID_SELECT])

    # Entity type select
    if built_in.get(BUILT_IN_ENTITY_TYPE_SELECT) is None:
        built_in[BUILT_IN_ENTITY_TYPE_SELECT] = create_input_select_entity(
            f"{DOMAIN}_{BUILT_IN_ENTITY_TYPE_SELECT}",
            {
                CONF_NAME: f"{TITLE} Entity Type",
                CONF_ICON: "mdi:puzzle",
                CONF_OPTIONS: ENTITY_TYPES
            },
        )
        to_add.append(built_in[BUILT_IN_ENTITY_TYPE_SELECT])

    await platform.async_add_entities(to_add)


class CustomInputSelect(InputSelect):
    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass