"""Base Integration class."""
import logging
from typing import Dict, List, Optional, Type, TypedDict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class AreaSettingsEntry(TypedDict):
    """Model for area settings stored in the store."""

    name: str
    icon: str
    original_name: str
    sort_order: int
    visible: bool


class AreaSettings(AreaSettingsEntry):
    """Model for area settings stored in IntegrationBase."""

    id: str


AreaSettingsRegistry = Dict[str, AreaSettingsEntry]


class EntitySettingsEntry(TypedDict):
    """Model for entity settings stored in the store."""

    area_id: str
    original_area_id: str
    name: str
    type: str
    original_type: str
    sort_order: int
    visible: bool


class EntitySettings(EntitySettingsEntry):
    """Model for entity settings stored in IntegrationBase."""

    entity_id: str


EntitySettingsRegistry = Dict[str, EntitySettingsEntry]


class Configuration:
    """Configuration class."""

    config: dict = {}
    config_entry: dict = {}
    config_type: Optional[str] = None
    lovelace_mode: Optional[str] = None
    missing_resources: List[str] = []


class IntegrationBase:
    """Base Integration class."""

    hass: HomeAssistant = None
    log = logging.getLogger(f"custom_components.{DOMAIN}")

    areas: List[AreaSettings] = []
    built_in_entities: Dict[str, Type[Entity]] = {}
    configuration: Configuration = None
    counters: List[str] = []
    entities: List[EntitySettings] = []
