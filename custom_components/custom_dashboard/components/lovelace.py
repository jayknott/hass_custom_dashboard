import logging
import os

from custom_components.hacs.api.hacs_repository import hacs_repository
from custom_components.hacs.api.hacs_repository_data import hacs_repository_data
from custom_components.hacs.share import get_hacs
from homeassistant.components.frontend import (
    async_register_built_in_panel,
    async_remove_panel,
    DATA_PANELS,
)
from homeassistant.components.lovelace import CONF_DASHBOARDS
from homeassistant.components.lovelace.dashboard import LovelaceYAML
from homeassistant.components.lovelace.const import (
    CONF_ICON,
    CONF_MODE,
    CONF_REQUIRE_ADMIN,
    CONF_RESOURCE_TYPE_WS,
    CONF_RESOURCES,
    CONF_SHOW_IN_SIDEBAR,
    CONF_TITLE,
    DOMAIN as LOVELACE_DOMAIN,
    MODE_STORAGE,
    MODE_YAML,
)
from homeassistant.const import (
    CONF_FILENAME,
    CONF_URL,
)

# from .binary_sensor import update_built_in_binary_sensors
from ..const import (
    CONF_MISSING_RESOURCES,
    DOMAIN,
    HACS_CUSTOM_REPOSITORIES,
    HACS_INTEGRATIONS,
    HACS_PLUGINS,
    LOVELACE_CUSTOM_CARDS,
    LOVELACE_DASHBOARD_ICON,
    LOVELACE_DASHBOARD_URL_PATH,
    LOVELACE_DIR,
    LOVELACE_FILENAME_SOURCE,
    LOVELACE_RESOURCE_TYPE_MODULE,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)


async def update_hacs(hass, hacs):
    # Add custom repositories to HACS
    for repo in HACS_CUSTOM_REPOSITORIES:
        hacs_repository_data(
            hass, None, {"repository": repo["url"], "action": "add", "data": "plugin"}
        )

    # Install needed HACS integrations and plugins
    for hacs_plugin in HACS_INTEGRATIONS + HACS_PLUGINS:
        try:
            repo = hacs.get_by_name(hacs_plugin)
            try:
                hacs_repository(
                    hass, None, {"repository": repo.data.id, "action": "install"}
                )
            except:
                _LOGGER.error("Unable to install HACS repository: %s", hacs_plugin)
        except:
            _LOGGER.warning(
                f"Could not connect to HACS install '{hacs_plugin}', will assume everything is okay."
            )


async def add_resource_module(hass, mode, resources, url):
    for resource in resources.async_items():
        if resource[CONF_URL] == url:
            # Item is already in the list
            return

    if mode == MODE_STORAGE:
        await resources.async_create_item(
            {CONF_URL: url, CONF_RESOURCE_TYPE_WS: LOVELACE_RESOURCE_TYPE_MODULE}
        )
    else:
        _LOGGER.error(
            f"{url} is not in the lovelace:resources list in the configuration.yaml"
        )
        hass.data[DOMAIN][CONF_MISSING_RESOURCES].append(url)


async def update_resources(hass, hacs, config):
    mode = config.get(CONF_MODE, MODE_STORAGE)
    resources = hass.data[LOVELACE_DOMAIN][CONF_RESOURCES]

    # Reset missing resources
    hass.data[DOMAIN][CONF_MISSING_RESOURCES] = []

    # Add the HACS plugins to the list
    for hacs_plugin in HACS_PLUGINS:
        try:
            repo = hacs.get_by_name(hacs_plugin)

            try:
                url = f"/hacsfiles/{hacs_plugin.split('/')[-1]}/{repo.data.file_name}"
                await add_resource_module(hass, mode, resources, url)
            except:
                _LOGGER.error(
                    f"Unable to add {hacs_plugin} the the Lovelace resource list.",
                    hacs_plugin,
                )
                hass.data[DOMAIN][CONF_MISSING_RESOURCES].append(url)
        except:
            _LOGGER.warning(
                f"Could not connect to HACS to check repository for '{hacs_plugin}', will assume everything is okay."
            )

    # Add custom cards to the list
    for card in LOVELACE_CUSTOM_CARDS:
        url = (
            f"/local/{LOVELACE_DASHBOARD_URL_PATH}/{card['dirname']}/{card['filename']}"
        )
        await add_resource_module(hass, mode, resources, url)


async def update_dashboards(hass):
    config = {
        CONF_MODE: MODE_YAML,
        CONF_TITLE: TITLE,
        CONF_ICON: LOVELACE_DASHBOARD_ICON,
        CONF_SHOW_IN_SIDEBAR: True,
        CONF_REQUIRE_ADMIN: False,
        CONF_FILENAME: os.path.join(
            os.path.dirname(__file__), LOVELACE_DIR, LOVELACE_FILENAME_SOURCE
        ),
    }

    yaml_config = LovelaceYAML(hass, LOVELACE_DASHBOARD_URL_PATH, config)
    hass.data[LOVELACE_DOMAIN][CONF_DASHBOARDS][
        LOVELACE_DASHBOARD_URL_PATH
    ] = yaml_config

    kwargs = {
        "frontend_url_path": LOVELACE_DASHBOARD_URL_PATH,
        "require_admin": config[CONF_REQUIRE_ADMIN],
        "config": {CONF_MODE: config[CONF_MODE]},
        "update": False,
        "sidebar_title": config[CONF_TITLE],
        "sidebar_icon": config[CONF_ICON],
    }

    if LOVELACE_DASHBOARD_URL_PATH in hass.data.get(DATA_PANELS, {}):
        async_remove_panel(hass, LOVELACE_DASHBOARD_URL_PATH)

    async_register_built_in_panel(hass, LOVELACE_DOMAIN, **kwargs)

    # Refresh lovelace using browser_mod
    hass.async_create_task(hass.services.async_call("browser_mod", "lovelace_reload"))


async def update_lovelace(hass, config):
    ll_config = config.get(LOVELACE_DOMAIN, {})
    hacs = get_hacs()

    # await update_hacs(hass, hacs)
    await update_resources(hass, hacs, ll_config)
    await update_dashboards(hass)
