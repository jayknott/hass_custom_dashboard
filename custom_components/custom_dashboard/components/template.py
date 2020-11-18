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
    CONF_MISSING_RESOURCES,
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
from ..share import get_base


async def setup_template() -> None:
    """Setup the template options."""

    base = get_base()
    hass = base.hass

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
        LOVELACE: os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, LOVELACE_DIR)
        ),
        CONF_MISSING_RESOURCES: base.configuration.missing_resources,
    }
    jinja.globals[JINJA_VARIABLE_BUILT_IN_ENTITIES] = BUILT_IN_ENTITY_IDS
    jinja.globals[JINJA_VARIABLE_SERVICES] = SERVICE_IDS

    await update_template_areas_global()
    await update_template_entities_global()


async def update_template_areas_global() -> None:
    """Update the area global with new data from the intergrations HA data."""

    base = get_base()

    jinja: TemplateEnvironment = base.hass.data.get(_ENVIRONMENT)
    jinja.globals[JINJA_VARIABLE_AREAS] = base.areas


async def update_template_entities_global() -> None:
    """Update the entities global with new data from the intergrations HA data."""

    base = get_base()

    jinja: TemplateEnvironment = base.hass.data.get(_ENVIRONMENT)
    jinja.globals[JINJA_VARIABLE_ENTITIES] = base.entities
