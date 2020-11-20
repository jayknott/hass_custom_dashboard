"""Services available for this integration."""
from homeassistant.core import ServiceCall

from .components.counters import update_counters
from .settings import (
    save_setting,
    SCHEMA_UPDATE_AREA_SERVICE,
    SCHEMA_UPDATE_ENTITY_SERVICE,
)
from .const import (
    CONF_AREA,
    CONF_ENTITY,
    DOMAIN,
    SERVICE_REBUILD_COUNTERS,
    SERVICE_SET_AREA,
    SERVICE_SET_ENTITY,
)
from .share import get_base


async def setup_services() -> None:
    """Setup services."""

    base = get_base()
    hass = base.hass
    register = get_base().hass.services.async_register

    async def service_rebuild_counters(call: ServiceCall) -> None:
        await update_counters()
        hass.async_create_task(
            hass.services.async_call("browser_mod", "lovelace_reload")
        )

    async def service_save_area_setting(call: ServiceCall) -> None:
        await save_setting(CONF_AREA, call)

    async def service_save_entity_setting(call: ServiceCall) -> None:
        await save_setting(CONF_ENTITY, call)

    # Rebuild counters
    register(DOMAIN, SERVICE_REBUILD_COUNTERS, service_rebuild_counters)

    # Set area settings service
    register(
        DOMAIN, SERVICE_SET_AREA, service_save_area_setting, SCHEMA_UPDATE_AREA_SERVICE
    )

    # Set entity settings service
    register(
        DOMAIN,
        SERVICE_SET_ENTITY,
        service_save_entity_setting,
        SCHEMA_UPDATE_ENTITY_SERVICE,
    )
