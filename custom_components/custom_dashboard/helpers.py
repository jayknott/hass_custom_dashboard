from homeassistant.const import CONF_TYPE, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity, async_generate_entity_id

from .const import DOMAIN


def generate_id(hass, domain, deviceID):
    return async_generate_entity_id(f"{domain}.{{}}", deviceID, hass=hass)


class CustomEntity(Entity):
    def __init__(self, hass, deviceID):
        self.hass = hass
        self.deviceID = deviceID
        self._state = STATE_UNKNOWN
        self._data = {}
        self.entity_id = generate_id(hass, self.domain, deviceID)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = STATE_UNKNOWN if state is None else state
        self.schedule_update_ha_state()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = {} if data is None else data
        self.schedule_update_ha_state()

    def update_data(self, data):
        self._data.update({} if data is None else data)
        self.schedule_update_ha_state()

    @property
    def device_id(self):
        return self.deviceID

    @property
    def device_state_attributes(self):
        return {CONF_TYPE: DOMAIN, **self.data}
