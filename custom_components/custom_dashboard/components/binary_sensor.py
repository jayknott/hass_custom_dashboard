"""Binary sensors helper."""
from homeassistant.components.template.binary_sensor import (
    BinarySensorTemplate,
    CONF_ATTRIBUTE_TEMPLATES,
    _async_create_entities,
)
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_SENSORS,
    CONF_VALUE_TEMPLATE,
)

from ..const import PLATFORM_BINARY_SENSOR
from ..share import get_base

PLATFORM = PLATFORM_BINARY_SENSOR


async def create_binary_sensor_entity(
    device_id: str, conf: dict = {}
) -> BinarySensorTemplate:
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

    entity: BinarySensorTemplate = (
        await _async_create_entities(get_base().hass, config)
    )[0]
    entity.entity_id = f"{PLATFORM}.{device_id}"

    return entity
