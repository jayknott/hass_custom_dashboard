"""Input selects used for settings."""
from typing import List

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
from homeassistant.helpers.entity_platform import EntityPlatform

from ..const import (
    CONF_ENTITY_PLATFORM,
    BUILT_IN_AREA_SELECT,
    BUILT_IN_ENTITY_AREA_SELECT,
    BUILT_IN_ENTITY_ID_SELECT,
    BUILT_IN_ENTITY_TYPE_SELECT,
    DOMAIN,
    ENTITY_TYPES,
    PLATFORM_INPUT_SELECT,
    TITLE,
)
from ..share import get_base

PLATFORM = PLATFORM_INPUT_SELECT


class CustomInputSelect(InputSelect):
    """Input select that removes stored states."""

    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass


async def setup_input_selects() -> None:
    """Setup input selects."""

    await update_input_selects()


async def update_input_selects() -> None:
    """Update built in input selects."""

    base = get_base()
    built_in = base.built_in_entities
    platform: EntityPlatform = base.hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add: List[CustomInputSelect] = []

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
                CONF_OPTIONS: ENTITY_TYPES,
            },
        )
        to_add.append(built_in[BUILT_IN_ENTITY_TYPE_SELECT])

    await platform.async_add_entities(to_add)


def create_input_select_entity(device_id: str, conf: dict = {}) -> CustomInputSelect:
    """Create a CustomInputSelect instance."""

    config = {
        CONF_ID: device_id,
        CONF_NAME: device_id,
        CONF_ICON: "mdi:form-textbox",
        CONF_OPTIONS: [""],
    }
    config.update(conf)

    entity = CustomInputSelect.from_yaml(config)

    return entity
