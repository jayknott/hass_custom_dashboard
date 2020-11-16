import logging

from homeassistant.components.input_text import (
    CONF_INITIAL,
    CONF_MAX,
    CONF_MAX_VALUE,
    CONF_MIN,
    CONF_MIN_VALUE,
    CONF_PATTERN,
    InputText,
    MODE_TEXT,
)
from homeassistant.const import (
    CONF_ICON,
    CONF_ID,
    CONF_MODE,
    CONF_NAME,
)
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_ENTITY_PLATFORM,
    BUILT_IN_AREA_ICON,
    BUILT_IN_AREA_NAME,
    CONF_BUILT_IN_ENTITIES,
    DOMAIN,
    PLATFORM_INPUT_TEXT,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM = PLATFORM_INPUT_TEXT


def create_input_text_entity(device_id, conf={}):
    entity_id = f"{PLATFORM}.{device_id}"
    config = {
        CONF_ID: entity_id.split(".")[-1],
        CONF_NAME: entity_id.split(".")[-1],
        CONF_MIN: CONF_MIN_VALUE,
        CONF_MAX: CONF_MAX_VALUE,
        CONF_PATTERN: None,
        CONF_ICON: "mdi:form-textbox",
        CONF_MODE: MODE_TEXT,
        CONF_INITIAL: "",
    }
    config.update(conf)

    entity = CustomInputText.from_yaml(config)

    return entity


async def update_built_in_input_text(hass):
    data = hass.data[DOMAIN]
    built_in = data[CONF_BUILT_IN_ENTITIES]
    platform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add = []

    # Area icon setting
    if built_in.get(BUILT_IN_AREA_ICON) is None:
        built_in[BUILT_IN_AREA_ICON] = create_input_text_entity(
            f"{DOMAIN}_{BUILT_IN_AREA_ICON}",
            {CONF_NAME: f"{TITLE} Area Icon", CONF_ICON: "mdi:crop-free"},
        )
        to_add.append(built_in[BUILT_IN_AREA_ICON])

    # Area name setting
    if built_in.get(BUILT_IN_AREA_NAME) is None:
        built_in[BUILT_IN_AREA_NAME] = create_input_text_entity(
            f"{DOMAIN}_{BUILT_IN_AREA_NAME}",
            {CONF_NAME: f"{TITLE} Area Name", CONF_ICON: "mdi:rename-box"},
        )
        to_add.append(built_in[BUILT_IN_AREA_NAME])

    await platform.async_add_entities(to_add)


class CustomInputText(InputText):
    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass