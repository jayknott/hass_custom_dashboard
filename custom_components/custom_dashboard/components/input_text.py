"""Input texts used for settings."""
from typing import List

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
from homeassistant.helpers.entity_platform import EntityPlatform

from ..const import (
    CONF_ENTITY_PLATFORM,
    BUILT_IN_AREA_ICON,
    BUILT_IN_AREA_NAME,
    DOMAIN,
    PLATFORM_INPUT_TEXT,
    TITLE,
)
from ..share import get_base

PLATFORM = PLATFORM_INPUT_TEXT


class CustomInputText(InputText):
    """Input text that removes stored states."""

    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass


async def setup_input_texts() -> None:
    """Setup input texts."""

    await update_input_texts()


async def update_input_texts() -> None:
    """Update built in input texts."""

    base = get_base()
    built_in = base.built_in_entities
    platform: EntityPlatform = base.hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add: List[CustomInputText] = []

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


def create_input_text_entity(device_id: str, conf: dict = {}) -> CustomInputText:
    """Create a CustomInputText instance."""

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