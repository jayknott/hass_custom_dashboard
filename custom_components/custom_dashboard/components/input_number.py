"""Input numbers used for settings."""
from typing import List

from homeassistant.components.input_number import (
    CONF_INITIAL,
    CONF_MAX,
    CONF_MIN,
    CONF_STEP,
    InputNumber,
    MODE_BOX,
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
    BUILT_IN_AREA_SORT_ORDER,
    BUILT_IN_ENTITY_SORT_ORDER,
    DEFAULT_SORT_ORDER,
    DEFAULT_SORT_ORDER_MAX,
    DEFAULT_SORT_ORDER_MIN,
    DOMAIN,
    PLATFORM_INPUT_NUMBER,
    TITLE,
)
from ..share import get_base

PLATFORM = PLATFORM_INPUT_NUMBER


class CustomInputNumber(InputNumber):
    """Input number that removes stored states."""

    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass


async def setup_input_numbers() -> None:
    """Setup input numbers."""

    await update_input_numbers()


async def update_input_numbers() -> None:
    """Update built in input numbers."""

    base = get_base()
    built_in = base.built_in_entities
    platform: EntityPlatform = base.hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add: List[CustomInputNumber] = []

    # Area sort order
    if built_in.get(BUILT_IN_AREA_SORT_ORDER) is None:
        built_in[BUILT_IN_AREA_SORT_ORDER] = create_input_number_entity(
            f"{DOMAIN}_{BUILT_IN_AREA_SORT_ORDER}",
            {
                CONF_NAME: f"{TITLE} Area Sort Order",
                CONF_ICON: "mdi:sort-numeric-ascending",
            },
        )
        to_add.append(built_in[BUILT_IN_AREA_SORT_ORDER])

    # Entity sort order
    if built_in.get(BUILT_IN_ENTITY_SORT_ORDER) is None:
        built_in[BUILT_IN_ENTITY_SORT_ORDER] = create_input_number_entity(
            f"{DOMAIN}_{BUILT_IN_ENTITY_SORT_ORDER}",
            {
                CONF_NAME: f"{TITLE} Entity Sort Order",
                CONF_ICON: "mdi:sort-numeric-ascending",
            },
        )
        to_add.append(built_in[BUILT_IN_ENTITY_SORT_ORDER])

    await platform.async_add_entities(to_add)


def create_input_number_entity(device_id: str, conf: dict = {}) -> CustomInputNumber:
    """Create a CustomInputNumber instance."""

    entity_id = f"{PLATFORM}.{device_id}"
    config = {
        CONF_ID: entity_id.split(".")[-1],
        CONF_NAME: entity_id.split(".")[-1],
        CONF_MIN: DEFAULT_SORT_ORDER_MIN,
        CONF_MAX: DEFAULT_SORT_ORDER_MAX,
        CONF_STEP: 1,
        CONF_ICON: None,
        CONF_MODE: MODE_BOX,
        CONF_INITIAL: DEFAULT_SORT_ORDER,
    }
    config.update(conf)

    entity = CustomInputNumber.from_yaml(config)

    return entity
