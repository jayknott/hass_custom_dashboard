"""Setup Custom Dashboard Services"""
from homeassistant.core import HomeAssistant, ServiceCall

from .settings import (
    save_setting,
    SCHEMA_UPDATE_AREA_SERVICE,
    SCHEMA_UPDATE_ENTITY_SERVICE,
)
from .const import (
    CONF_AREA,
    CONF_ENTITY,
    DOMAIN,
    SERVICE_SET_AREA,
    SERVICE_SET_ENTITY,
)


async def setup_services(hass: HomeAssistant) -> None:
    async def service_save_area_setting(call: ServiceCall) -> None:
        await save_setting(hass, CONF_AREA, call)

    async def service_save_entity_setting(call: ServiceCall) -> None:
        await save_setting(hass, CONF_ENTITY, call)

    # Set area settings service
    hass.services.async_register(
        DOMAIN, SERVICE_SET_AREA, service_save_area_setting, SCHEMA_UPDATE_AREA_SERVICE
    )

    # Set entity settings service
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ENTITY,
        service_save_entity_setting,
        SCHEMA_UPDATE_ENTITY_SERVICE,
    )
