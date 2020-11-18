"""Automations used in the integration."""
from typing import List

from homeassistant.components.automation import (
    AutomationEntity,
    CONF_ACTION,
    CONF_INITIAL_STATE,
    CONF_TRIGGER,
)
from homeassistant.components.homeassistant.triggers.event import CONF_EVENT_TYPE
from homeassistant.components.input_select import CONF_OPTIONS
from homeassistant.const import (
    ATTR_AREA_ID,
    ATTR_NAME,
    CONF_ALIAS,
    CONF_ENTITY_ID,
    CONF_ICON,
    CONF_ID,
    CONF_MODE,
    CONF_PLATFORM,
    CONF_SERVICE,
    CONF_SERVICE_TEMPLATE,
    CONF_TYPE,
    CONF_VARIABLES,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import EntityPlatform
from homeassistant.helpers.script import (
    CONF_MAX,
    CONF_MAX_EXCEEDED,
    SCRIPT_MODE_RESTART,
    Script,
)
from homeassistant.helpers.service import (
    CONF_SERVICE_DATA_TEMPLATE,
    CONF_SERVICE_ENTITY_ID,
)
from homeassistant.helpers.template import Template

from ..const import (
    BUILT_IN_AREA_SORT_ORDER,
    BUILT_IN_AREA_VISIBLE,
    BUILT_IN_ENTITY_AREA_SELECT,
    BUILT_IN_ENTITY_ID_SELECT,
    BUILT_IN_ENTITY_SORT_ORDER,
    BUILT_IN_ENTITY_TYPE_SELECT,
    BUILT_IN_ENTITY_VISIBLE,
    CONF_ENTITY_PLATFORM,
    BUILT_IN_AREA_ICON,
    BUILT_IN_AREA_NAME,
    BUILT_IN_AREA_SELECT,
    BUILT_IN_AUTOMATION_AREA_CHANGED,
    BUILT_IN_AUTOMATION_ENTITY_CHANGED,
    BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT,
    BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT,
    BUILT_IN_ENTITY_IDS,
    CONF_ORIGINAL_NAME,
    CONF_SORT_ORDER,
    CONF_VISIBLE,
    DEFAULT_SORT_ORDER,
    DOMAIN,
    EVENT_TRIGGER_AREA_AUTOMATIONS,
    EVENT_TRIGGER_ENTITY_AUTOMATIONS,
    JINJA_VARIABLE_AREAS,
    JINJA_VARIABLE_ENTITIES,
    PLATFORM_AUTOMATION,
    PLATFORM_INPUT_BOOLEAN,
    PLATFORM_INPUT_NUMBER,
    PLATFORM_INPUT_SELECT,
    PLATFORM_INPUT_TEXT,
    TITLE,
)
from ..share import get_base

PLATFORM = PLATFORM_AUTOMATION


class CustomAutomation(AutomationEntity):
    """Automation that removes stored states."""

    async def async_internal_added_to_hass(self):
        await Entity.async_internal_added_to_hass(self)

    async def async_internal_will_remove_from_hass(self):
        await Entity.async_internal_will_remove_from_hass(self)

    async def async_get_last_state(self):
        pass


async def setup_automations() -> None:
    """Setup automations."""

    await update_automations()


async def update_automations(force: bool = False):
    """Update built in automations."""

    base = get_base()
    hass = base.hass
    built_in = base.built_in_entities
    platform: EntityPlatform = hass.data[CONF_ENTITY_PLATFORM][PLATFORM][0]
    to_add: List[CustomAutomation] = []
    to_trigger: List[CustomAutomation] = []

    # Update area selectors
    if built_in.get(BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT) is None or force:
        if not force:
            built_in[
                BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT
            ] = create_automation_entity(
                f"{DOMAIN}_{BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT}",
                {
                    CONF_ALIAS: f"{TITLE} update Area Selector",
                    CONF_TRIGGER: [
                        {
                            CONF_PLATFORM: "event",
                            CONF_EVENT_TYPE: EVENT_TRIGGER_AREA_AUTOMATIONS,
                        },
                    ],
                    CONF_ACTION: [
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_SELECT}.set_options",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_AREA_SELECT
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "options": Template(
                                    f"""
                                        {{% set areas = {JINJA_VARIABLE_AREAS} %}}
                                        {{% if areas is not none and areas | length > 0 %}}
                                            {{{{ areas | map(attribute='{CONF_ORIGINAL_NAME}') | list }}}}
                                        {{% else %}}
                                            {{{{ [''] }}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_SELECT}.set_options",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_ENTITY_AREA_SELECT
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "options": Template(
                                    f"""
                                        {{% set areas = {JINJA_VARIABLE_AREAS} %}}
                                        {{% if areas is not none and areas | length > 0 %}}
                                            {{{{ [''] + (areas | map(attribute='{CONF_ORIGINAL_NAME}') | list) }}}}
                                        {{% else %}}
                                            {{{{ [''] }}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                    ],
                },
            )
        to_add.append(built_in[BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT])
        to_trigger.append(built_in[BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT])

    # Update entity id selectors
    if built_in.get(BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT) is None or force:
        if not force:
            built_in[
                BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT
            ] = create_automation_entity(
                f"{DOMAIN}_{BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT}",
                {
                    CONF_ALIAS: f"{TITLE} update entity selector",
                    CONF_TRIGGER: [
                        {
                            CONF_PLATFORM: "event",
                            CONF_EVENT_TYPE: EVENT_TRIGGER_ENTITY_AUTOMATIONS,
                        },
                    ],
                    CONF_ACTION: [
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_SELECT}.set_options",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_ENTITY_ID_SELECT
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "options": Template(
                                    f"""{{{{
                                        states |
                                        map(attribute='{CONF_ENTITY_ID}') |
                                        reject('regex_search', '\.{DOMAIN}_') |
                                        list
                                    }}}}""",
                                    hass,
                                )
                            },
                        }
                    ],
                },
            )
        to_add.append(built_in[BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT])
        to_trigger.append(built_in[BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT])

    # Update area setting controls on area change
    if built_in.get(BUILT_IN_AUTOMATION_AREA_CHANGED) is None or force:
        if not force:
            built_in[BUILT_IN_AUTOMATION_AREA_CHANGED] = create_automation_entity(
                f"{DOMAIN}_{BUILT_IN_AUTOMATION_AREA_CHANGED}",
                {
                    CONF_ALIAS: f"{TITLE} area selection changed",
                    CONF_TRIGGER: [
                        {
                            CONF_PLATFORM: "state",
                            CONF_ENTITY_ID: BUILT_IN_ENTITY_IDS[BUILT_IN_AREA_SELECT],
                        }
                    ],
                    CONF_ACTION: [
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_TEXT}.set_value",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_AREA_ICON
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "value": Template(
                                    f"""
                                        {{% set area = {JINJA_VARIABLE_AREAS} |
                                                        selectattr(
                                                            '{CONF_ORIGINAL_NAME}',
                                                            'equalto',
                                                            states('{BUILT_IN_ENTITY_IDS[BUILT_IN_AREA_SELECT]}')
                                                        ) |
                                                        first
                                        %}}
                                        {{% if area is not none %}}
                                            {{{{ area.{CONF_ICON} }}}}
                                        {{% else %}}
                                            {{{{ '' }}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_TEXT}.set_value",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_AREA_NAME
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "value": Template(
                                    f"""
                                        {{% set area = {JINJA_VARIABLE_AREAS} |
                                                        selectattr(
                                                            '{CONF_ORIGINAL_NAME}',
                                                            'equalto',
                                                            states('{BUILT_IN_ENTITY_IDS[BUILT_IN_AREA_SELECT]}')
                                                        ) |
                                                        first
                                        %}}
                                        {{% if area is not none %}}
                                            {{{{ area.{ATTR_NAME} }}}}
                                        {{% else %}}
                                            {{{{ '' }}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_NUMBER}.set_value",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_AREA_SORT_ORDER
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "value": Template(
                                    f"""
                                        {{% set area = {JINJA_VARIABLE_AREAS} |
                                                        selectattr(
                                                            '{CONF_ORIGINAL_NAME}',
                                                            'equalto',
                                                            states('{BUILT_IN_ENTITY_IDS[BUILT_IN_AREA_SELECT]}')
                                                        ) |
                                                        first
                                        %}}
                                        {{% if area is not none %}}
                                            {{{{ area.{CONF_SORT_ORDER} }}}}
                                        {{% else %}}
                                            {{{{ {DEFAULT_SORT_ORDER} }}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                        {
                            CONF_SERVICE_TEMPLATE: Template(
                                f"""
                                    {{% set area = {JINJA_VARIABLE_AREAS} |
                                                    selectattr(
                                                        '{CONF_ORIGINAL_NAME}',
                                                        'equalto',
                                                        states('{BUILT_IN_ENTITY_IDS[BUILT_IN_AREA_SELECT]}')
                                                    ) |
                                                    first
                                    %}}
                                    {{% if area is not none and not area.{CONF_VISIBLE} %}}
                                        {PLATFORM_INPUT_BOOLEAN}.turn_off
                                    {{% else %}}
                                        {PLATFORM_INPUT_BOOLEAN}.turn_on
                                    {{% endif %}}
                                """,
                                hass,
                            ),
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_AREA_VISIBLE
                            ],
                        },
                    ],
                },
            )
        to_add.append(built_in[BUILT_IN_AUTOMATION_AREA_CHANGED])

    # Update entity setting controls on entity change
    if built_in.get(BUILT_IN_AUTOMATION_ENTITY_CHANGED) is None or force:
        if not force:
            built_in[BUILT_IN_AUTOMATION_ENTITY_CHANGED] = create_automation_entity(
                f"{DOMAIN}_{BUILT_IN_AUTOMATION_ENTITY_CHANGED}",
                {
                    CONF_ALIAS: f"{TITLE} entity selection changed",
                    CONF_TRIGGER: [
                        {
                            CONF_PLATFORM: "state",
                            CONF_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_ENTITY_ID_SELECT
                            ],
                        }
                    ],
                    CONF_ACTION: [
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_SELECT}.select_option",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_ENTITY_AREA_SELECT
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "option": Template(
                                    f"""
                                        {{% set area_id =
                                            ({JINJA_VARIABLE_ENTITIES} |
                                                selectattr(
                                                    '{CONF_ENTITY_ID}',
                                                    'equalto',
                                                    states('{BUILT_IN_ENTITY_IDS[BUILT_IN_ENTITY_ID_SELECT]}')
                                                ) |
                                                list |
                                                first
                                            ).{ATTR_AREA_ID}
                                        %}}
                                        {{% set area = {JINJA_VARIABLE_AREAS} | selectattr('{CONF_ID}', 'equalto', area_id) | list %}}
                                        {{% if (area | length) > 0 %}}
                                            {{{{- (area | first).{CONF_ORIGINAL_NAME} -}}}}
                                        {{% else %}}
                                            {{{{- '' -}}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_SELECT}.select_option",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_ENTITY_TYPE_SELECT
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "option": Template(
                                    f"""
                                        {{% set entity_type =
                                            ({JINJA_VARIABLE_ENTITIES} |
                                                selectattr(
                                                    '{CONF_ENTITY_ID}',
                                                    'equalto',
                                                    states('{BUILT_IN_ENTITY_IDS[BUILT_IN_ENTITY_ID_SELECT]}')
                                                ) |
                                                list |
                                                first
                                            ).{CONF_TYPE}
                                        %}}
                                        {{% if entity_type in state_attr('{BUILT_IN_ENTITY_IDS[BUILT_IN_ENTITY_TYPE_SELECT]}', '{CONF_OPTIONS}') %}}
                                            {{{{ entity_type }}}}
                                        {{% else %}}
                                            {{{{ '' }}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                        {
                            CONF_SERVICE: f"{PLATFORM_INPUT_NUMBER}.set_value",
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_ENTITY_SORT_ORDER
                            ],
                            CONF_SERVICE_DATA_TEMPLATE: {
                                "value": Template(
                                    f"""
                                        {{% set entity =
                                            ({JINJA_VARIABLE_ENTITIES} |
                                                selectattr(
                                                    '{CONF_ENTITY_ID}',
                                                    'equalto',
                                                    states('{BUILT_IN_ENTITY_IDS[BUILT_IN_ENTITY_ID_SELECT]}')
                                                ) |
                                                list |
                                                first)
                                        %}}
                                        {{% if entity is not none %}}
                                            {{{{ entity.{CONF_SORT_ORDER} }}}}
                                        {{% else %}}
                                            {{{{ {DEFAULT_SORT_ORDER} }}}}
                                        {{% endif %}}
                                    """,
                                    hass,
                                )
                            },
                        },
                        {
                            CONF_SERVICE_TEMPLATE: Template(
                                f"""
                                    {{% set entity =
                                        ({JINJA_VARIABLE_ENTITIES} |
                                            selectattr(
                                                '{CONF_ENTITY_ID}',
                                                'equalto',
                                                states('{BUILT_IN_ENTITY_IDS[BUILT_IN_ENTITY_ID_SELECT]}')
                                            ) |
                                            list |
                                            first)
                                    %}}
                                    {{% if entity is not none and not entity.{CONF_VISIBLE} %}}
                                        {PLATFORM_INPUT_BOOLEAN}.turn_off
                                    {{% else %}}
                                        {PLATFORM_INPUT_BOOLEAN}.turn_on
                                    {{% endif %}}
                                """,
                                hass,
                            ),
                            CONF_SERVICE_ENTITY_ID: BUILT_IN_ENTITY_IDS[
                                BUILT_IN_ENTITY_VISIBLE
                            ],
                        },
                    ],
                },
            )
        to_add.append(built_in[BUILT_IN_AUTOMATION_ENTITY_CHANGED])

    await platform.async_add_entities(to_add)

    for entity in to_trigger:
        hass.async_create_task(entity.async_trigger({}))


def create_automation_entity(device_id: str, conf: dict = {}) -> CustomAutomation:
    """Create a CustomAutomation instance."""

    base = get_base()

    entity_id = f"{PLATFORM}.{device_id}"
    alias: str = conf.get(CONF_ALIAS, entity_id.split(".")[-1])

    entity = CustomAutomation(
        conf.get(CONF_ID, entity_id.split(".")[-1]),
        alias,
        conf.get(CONF_TRIGGER),
        None,  # Not supporting contitions at this time
        Script(
            base.hass,
            conf.get(CONF_ACTION),
            alias,
            PLATFORM_AUTOMATION,
            running_description="automation actions",
            script_mode=conf.get(CONF_MODE, SCRIPT_MODE_RESTART),
            max_runs=conf.get(CONF_MAX),
            max_exceeded=conf.get(CONF_MAX_EXCEEDED),
            logger=base.log,
        ),
        conf.get(CONF_INITIAL_STATE),
        conf.get(CONF_VARIABLES),
    )
    entity.entity_id = entity_id
    entity.editable = False

    return entity