from homeassistant.const import (
    CONF_DEFAULT,
    STATE_CLOSED,
    STATE_LOCKED,
    STATE_PLAYING,
)

#################################################
### Constants that need to be changed per project
#################################################

# Title displayed in the panel list
TITLE = "Custom Dashboard"

# Icon displayed in the panel list
LOVELACE_DASHBOARD_ICON = "mdi:view-dashboard"

# Icon to display by default for rooms
DEFAULT_ROOM_ICON = "mdi:square-rounded-outline"

# List of repositories that need to be imported into HACS [{"url": str, "type": "plugin"}]
HACS_CUSTOM_REPOSITORIES = [
    {"url": "https://github.com/DBuit/light-popup-card", "type": "plugin"},
]

# HACS integration repositories to install. This needs to be the full name.
#   Make sure any custom repositories are included in both HACS_CUSTOM_REPOSITORIES and this list
HACS_INTEGRATIONS = ["thomasloven/hass-browser_mod"]

# HACS plugin repositories to install. This needs to be the full name.
#   Make sure any custom repositories are included in both HACS_CUSTOM_REPOSITORIES and this list
HACS_PLUGINS = [
    "custom-cards/button-card",
    "DBuit/light-popup-card",
    "ljmerza/light-entity-card",
    "thomasloven/lovelace-card-mod",
    "kalkih/mini-media-player",
]

# Custom cards that needs to be imported. These needs to be stored in ./lovelace/cards/[dirname].
#   In the format of {"dirname": str, "filename": str}.
#   File must be in the root of the directory.
LOVELACE_CUSTOM_CARDS = [
    {
        "dirname": "custom-dashboard-flexbox-card",
        "filename": "custom-dashboard-flexbox-card.js",
    },
]

# Default translation to use if there is no translation for the user's current HA selected language.
DATA_DEFAULT_LANGUAGE = "en"

# Additional variables to include in the Jinja object
JINJA_VARIABLES = {}

# Supported entity types (These can be anything the dashboard will support and track)
# Does not need to be specific to HA integrations.
# The next few constants will map HA integrations to these entity types.
ENTITY_TYPES = [
    "",
    "all_lights",
    "battery",
    "camera",
    "climate",
    "climate_main",
    "humidity",
    "light",
    "lock",
    "media_player",
    "media_player_no_volume",
    "motion",
    "opening",
    "remote",
    "remote_button",
    "sensor",
    "switch",
    "temperature",
    "vacuum",
    "weather",
]

# Entity types that can be linked to the security of a home
# These can be duplicated from the ENTITY_TYPES to create entities
# that are associated with security of the home or not.
# Groups will be created with a 'security' prefix for each area and
# entity type/area combination for tracking.
SECURITY_ENTITY_TYPES = [
    "lock",
    "motion",
    "opening",
    "sensor",
]

# Map OFF states (array) for security entity types. This will allow easier tracking
# for a security entity that is in an unsecured state. Do not included entity
# types that use ON and OFF by default.
SECURITY_ENTITY_TYPE_OFF_STATES = {
    "lock": [STATE_LOCKED],
    "opening": [STATE_CLOSED],
}

# Entity types that are tracked globally and per area.
# A group will be created for each entity type and entity type/area
# combination so tracking and notifications can be done. You don't need
# to include it here if it is also included in SOMETHING_ON_ENTITY_TYPES.
TRACKED_ENTITY_TYPES = [
    "light",
    "motion",
]

# Map ON states (array) for tracked entity types. This will allow easier tracking
# for an entity that is in an ON state. Do not included entity types that
# use ON and OFF by default. This applied to TRACKED_ENTITY_TYPES and
# SOMETHING_ON_ENTITY_TYPES
TRACKED_ENTITY_TYPE_ON_STATES = {
    "media_player": [STATE_PLAYING],
}

# Group tracked entities together to track if something is on globally
# or in an area. This is useful if the dashboard tracks lights
# and all other entities seperately.
# This must be a subset of TRACKED_ENTITY_TYPES, but can be an empty array.
SOMETHING_ON_ENTITY_TYPES = [
    "media_player",
    "remote",
    "switch",
]

# The device classes for binary sensors that will be automatically mapped to an entity type
BINARY_SENSOR_CLASS_MAP = {
    "battery": "battery",
    "door": "security_opening",
    "garage_door": "security_opening",
    "light": "light",
    "motion": "motion",
    "occupancy": "motion",
    "safety": "security_sensor",
    "window": "security_opening",
    CONF_DEFAULT: "sensor",
}

# The device classes for sensors that will be automatically mapped to an entity type
SENSOR_CLASS_MAP = {
    "battery": "battery",
    "humidity": "humidity",
    "temperature": "temperature",
    CONF_DEFAULT: "sensor",
}

COVER_CLASS_MAP = {
    "door": "security_opening",
    "garage": "security_opening",
    "gate": "security_opening",
    "window": "security_opening",
    CONF_DEFAULT: "opening",
}

# Platforms that will be automatically mapped to and entity type
# Binary Sensor, Cover, and Sensor are all ready covered by the CONF_DEFAULT
# value in their maps.
PLATFORM_MAP = {
    "lock": "security_lock",
}

###########################################
### These constants should not be touched.
###########################################

DOMAIN = f"{TITLE.lower().replace(' ', '_').replace('-', '_')}"

PLATFORM_AUTOMATION = "automation"
PLATFORM_BINARY_SENSOR = "binary_sensor"
PLATFORM_GROUP = "group"
PLATFORM_INPUT_BOOLEAN = "input_boolean"
PLATFORM_INPUT_NUMBER = "input_number"
PLATFORM_INPUT_SELECT = "input_select"
PLATFORM_INPUT_TEXT = "input_text"

BUILT_IN_AREA_ICON = "area_icon"
BUILT_IN_AREA_NAME = "area_name"
BUILT_IN_AREA_SELECT = "area_select"
BUILT_IN_AREA_SELECTED = "selected_area"
BUILT_IN_AREA_SORT_ORDER = "area_sort_order"
BUILT_IN_AREA_VISIBLE = "area_visible"
BUILT_IN_AUTOMATION_AREA_CHANGED = "automation_area_changed"
BUILT_IN_AUTOMATION_ENTITY_CHANGED = "automation_entity_changed"
BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT = "automation_populate_area_select"
BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT = "automation_populate_entity_select"
BUILT_IN_ENTITY_AREA_SELECT = "entity_area_select"
BUILT_IN_ENTITY_ID_SELECT = "entity_id_select"
BUILT_IN_ENTITY_SELECTED = "selected_entity"
BUILT_IN_ENTITY_SORT_ORDER = "entity_sort_order"
BUILT_IN_ENTITY_TYPE_SELECT = "entity_type_select"
BUILT_IN_ENTITY_VISIBLE = "entity_visible"

BUILT_IN_ENTITY_IDS = {
    BUILT_IN_AREA_ICON: f"{PLATFORM_INPUT_TEXT}.{DOMAIN}_{BUILT_IN_AREA_ICON}",
    BUILT_IN_AREA_NAME: f"{PLATFORM_INPUT_TEXT}.{DOMAIN}_{BUILT_IN_AREA_NAME}",
    BUILT_IN_AREA_SELECT: f"{PLATFORM_INPUT_SELECT}.{DOMAIN}_{BUILT_IN_AREA_SELECT}",
    BUILT_IN_AREA_SELECTED: f"{PLATFORM_BINARY_SENSOR}.{DOMAIN}_{BUILT_IN_AREA_SELECTED}",
    BUILT_IN_AREA_SORT_ORDER: f"{PLATFORM_INPUT_NUMBER}.{DOMAIN}_{BUILT_IN_AREA_SORT_ORDER}",
    BUILT_IN_AREA_VISIBLE: f"{PLATFORM_INPUT_BOOLEAN}.{DOMAIN}_{BUILT_IN_AREA_VISIBLE}",
    BUILT_IN_AUTOMATION_AREA_CHANGED: f"{PLATFORM_AUTOMATION}.{DOMAIN}_{BUILT_IN_AUTOMATION_AREA_CHANGED}",
    BUILT_IN_AUTOMATION_ENTITY_CHANGED: f"{PLATFORM_AUTOMATION}.{DOMAIN}_{BUILT_IN_AUTOMATION_ENTITY_CHANGED}",
    BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT: f"{PLATFORM_AUTOMATION}.{DOMAIN}_{BUILT_IN_AUTOMATION_POPULATE_AREA_SELECT}",
    BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT: f"{PLATFORM_AUTOMATION}.{DOMAIN}_{BUILT_IN_AUTOMATION_POPULATE_ENTITY_SELECT}",
    BUILT_IN_ENTITY_AREA_SELECT: f"{PLATFORM_INPUT_SELECT}.{DOMAIN}_{BUILT_IN_ENTITY_AREA_SELECT}",
    BUILT_IN_ENTITY_ID_SELECT: f"{PLATFORM_INPUT_SELECT}.{DOMAIN}_{BUILT_IN_ENTITY_ID_SELECT}",
    BUILT_IN_ENTITY_SELECTED: f"{PLATFORM_BINARY_SENSOR}.{DOMAIN}_{BUILT_IN_ENTITY_SELECTED}",
    BUILT_IN_ENTITY_SORT_ORDER: f"{PLATFORM_INPUT_NUMBER}.{DOMAIN}_{BUILT_IN_ENTITY_SORT_ORDER}",
    BUILT_IN_ENTITY_TYPE_SELECT: f"{PLATFORM_INPUT_SELECT}.{DOMAIN}_{BUILT_IN_ENTITY_TYPE_SELECT}",
    BUILT_IN_ENTITY_VISIBLE: f"{PLATFORM_INPUT_BOOLEAN}.{DOMAIN}_{BUILT_IN_ENTITY_VISIBLE}",
}

CONF_ACTION = "action"
CONF_ADDERS = "adders"
CONF_AREA = "area"
CONF_AREA_NAME = "area_name"
CONF_AREAS = "areas"
CONF_COUNT = "count"
CONF_CREATE = "create"
CONF_BUILT_IN_ENTITIES = "built_in_entities"
CONF_CONFIG = "config"
CONF_ENTITIES = "entities"
CONF_ENTITY = "entity"
CONF_ENTITY_PLATFORM = "entity_platform"
CONF_MISSING_RESOURCES = "missing_resources"
CONF_ORIGINAL_AREA_ID = "original_area_id"
CONF_ORIGINAL_NAME = "original_name"
CONF_ORIGINAL_TYPE = "original_type"
CONF_REMOVE = "remove"
CONF_SECURITY = "security"
CONF_SELECTED_AREA = "selected_area"
CONF_SELECTED_ENTITY = "selected_entity"
CONF_SOMETHING_ON = "something_on"
CONF_SORT_ORDER = "sort_order"
CONF_TITLE = "title"
CONF_TRACKED_ENTITY_COUNT = "tracked_entity_count"
CONF_TRANSLATIONS = "translations"
CONF_UPDATE = "update"
CONF_VALUE = "value"
CONF_VISIBLE = "visible"

DEFAULT_SORT_ORDER = 500000
DEFAULT_SORT_ORDER_MAX = 999999
DEFAULT_SORT_ORDER_MIN = 1

EVENT_SETTINGS_CHANGED = f"{DOMAIN}_settings_changed"
EVENT_AREA_SETTINGS_CHANGED = f"{DOMAIN}_area_settings_changed"
EVENT_ENTITY_SETTINGS_CHANGED = f"{DOMAIN}_entity_settings_changed"
EVENT_TRIGGER_AREA_AUTOMATIONS = f"{DOMAIN}_trigger_area_automations"
EVENT_TRIGGER_ENTITY_AUTOMATIONS = f"{DOMAIN}_trigger_entity_automations"

LOVELACE = "lovelace"
LOVELACE_CARD_DIR = "cards"
LOVELACE_DASHBOARD_URL_PATH = DOMAIN.replace("_", "-")
LOVELACE_DIR = LOVELACE
LOVELACE_FILENAME_SOURCE = "ui-lovelace.yaml"
LOVELACE_FILENAME_DESTINATION = f"ui-lovelace-{LOVELACE_DASHBOARD_URL_PATH}.yaml"
LOVELACE_RESOURCE_TYPE_JS = "js"
LOVELACE_RESOURCE_TYPE_MODULE = "module"

SERVICE_SET_AREA = "set_area"
SERVICE_SET_ENTITY = "set_entity"
SERVICE_IDS = {
    SERVICE_SET_AREA: f"{DOMAIN}.{SERVICE_SET_AREA}",
    SERVICE_SET_ENTITY: f"{DOMAIN}.{SERVICE_SET_ENTITY}",
}

TRANSLATIONS_PATH = "translations/"

YAML_FILE = "!file"
YAML_INCLUDE = "!include"
YAML_TAG = f"# {DOMAIN}"

JINJA_VARIABLE_ADDITIONAL = f"_{DOMAIN}_variables"
JINJA_VARIABLE_AREAS = f"_{DOMAIN}_areas"
JINJA_VARIABLE_BUILT_IN_ENTITIES = f"_{DOMAIN}_built_in_entities"
JINJA_VARIABLE_CONFIGURATION = f"_{DOMAIN}_config"
JINJA_VARIABLE_ENTITIES = f"_{DOMAIN}_entities"
JINJA_VARIABLE_SERVICES = f"_{DOMAIN}_services"
JINJA_VARIABLE_TRANSLATE = f"_{DOMAIN}_trans"
JINJA_VARIABLE_USER_ID = f"_{DOMAIN}_user_id"
