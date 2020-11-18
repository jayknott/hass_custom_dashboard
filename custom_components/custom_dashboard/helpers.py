"""Helpers for this integration."""
from typing import Any, Optional
from homeassistant.const import CONF_TYPE, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity, async_generate_entity_id

from .const import DOMAIN
from .share import get_base


def generate_id(domain: str, deviceID: str) -> str:
    """Generates a unique ID for an entity."""

    return async_generate_entity_id(f"{domain}.{{}}", deviceID, get_base().hass)


class CustomEntity(Entity):
    """Base class for custom entities."""

    def __init__(self, deviceID: str):
        self.hass = get_base().hass
        self.deviceID = deviceID
        self._state = STATE_UNKNOWN
        self._data = {}
        self.entity_id = generate_id(self.domain, deviceID)

    @property
    def state(self) -> Any:
        return self._state

    @state.setter
    def state(self, state: Any) -> None:
        self._state = STATE_UNKNOWN if state is None else state
        self.schedule_update_ha_state()

    @property
    def data(self) -> Optional[dict]:
        return self._data

    @data.setter
    def data(self, data: Optional[dict]) -> None:
        self._data = {} if data is None else data
        self.schedule_update_ha_state()

    def update_data(self, data: Optional[dict]) -> None:
        self._data.update({} if data is None else data)
        self.schedule_update_ha_state()

    @property
    def device_id(self) -> str:
        return self.deviceID

    @property
    def device_state_attributes(self) -> dict:
        return {CONF_TYPE: DOMAIN, **self.data}
