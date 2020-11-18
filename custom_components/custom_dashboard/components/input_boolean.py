"""Input booleans used for settings."""
from typing import List

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
from homeassistant.helpers.entity_platform import EntityPlatform

from ..const import (
    CONF_ENTITY_PLATFORM,
    BUILT_IN_AREA_VISIBLE,
    BUILT_IN_ENTITY_VISIBLE,
    DOMAIN,
    PLATFORM_INPUT_BOOLEAN,
    TITLE,
)
from ..share import get_base

PLATFORM = PLATFORM_INPUT_BOOLEAN


class CustomInputBoolean(InputBoolean):
    """Input boolean that removes stored states."""

    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass


async def setup_input_booleans() -> None:
    """Setup input booleans."""

    await update_input_booleans()


async def update_input_booleans() -> None:
    """Update built in input booleans."""

    base = get_base()

    built_in = base.built_in_entities
    platform: EntityPlatform = base.hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add: List[CustomInputBoolean] = []

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


def create_input_boolean_entity(device_id: str, conf: dict = {}) -> CustomInputBoolean:
    """Create a CustomInputBoolean instance."""

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