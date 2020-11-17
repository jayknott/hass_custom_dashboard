"""Extend the template options for HA."""
import jinja2
import os
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import (
    _ENVIRONMENT,
    regex_match,
    regex_search,
    TemplateEnvironment,
)

from ..const import (
    BUILT_IN_ENTITY_IDS,
    CONF_AREAS,
    CONF_ENTITIES,
    CONF_MISSING_RESOURCES,
    DOMAIN,
    JINJA_VARIABLE_ADDITIONAL,
    JINJA_VARIABLE_AREAS,
    JINJA_VARIABLE_BUILT_IN_ENTITIES,
    JINJA_VARIABLE_CONFIGURATION,
    JINJA_VARIABLE_ENTITIES,
    JINJA_VARIABLE_SERVICES,
    JINJA_VARIABLES,
    LOVELACE,
    LOVELACE_DIR,
    SERVICE_IDS,
)


async def setup_template(hass: HomeAssistant) -> None:
    """Setup the template options."""

    jinja: Optional[TemplateEnvironment] = hass.data.get(_ENVIRONMENT)
    if jinja is None:
        jinja = hass.data[_ENVIRONMENT] = TemplateEnvironment(hass)

    jinja.loader = jinja2.FileSystemLoader("/")

    if jinja.tests.get("regex_match") is None:
        jinja.tests["regex_match"] = regex_match
    if jinja.tests.get("regex_search") is None:
        jinja.tests["regex_search"] = regex_search

    jinja.globals[JINJA_VARIABLE_ADDITIONAL] = JINJA_VARIABLES
    jinja.globals[JINJA_VARIABLE_CONFIGURATION] = {
        LOVELACE: os.path.join(os.path.dirname(__file__), LOVELACE_DIR),
        CONF_MISSING_RESOURCES: hass.data[DOMAIN][CONF_MISSING_RESOURCES],
    }
    jinja.globals[JINJA_VARIABLE_BUILT_IN_ENTITIES] = BUILT_IN_ENTITY_IDS
    jinja.globals[JINJA_VARIABLE_SERVICES] = SERVICE_IDS

    await update_template_areas_global(hass)
    await update_template_entities_global(hass)


async def update_template_areas_global(hass: HomeAssistant) -> None:
    """Update the area global with new data from the intergrations HA data."""

    jinja: TemplateEnvironment = hass.data.get(_ENVIRONMENT)
    jinja.globals[JINJA_VARIABLE_AREAS] = hass.data[DOMAIN][CONF_AREAS]


async def update_template_entities_global(hass: HomeAssistant) -> None:
    """Update the entities global with new data from the intergrations HA data."""

    jinja: TemplateEnvironment = hass.data.get(_ENVIRONMENT)
    jinja.globals[JINJA_VARIABLE_ENTITIES] = hass.data[DOMAIN][CONF_ENTITIES]
