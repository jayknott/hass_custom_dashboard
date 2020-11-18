"""Extend Lovelace to support this integration."""
import os
from typing import Type

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
from homeassistant.helpers.collection import StorageCollection
from homeassistant.helpers.typing import ConfigType

from ..const import (
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
from ..share import get_base


async def setup_lovelace() -> None:
    """Setup Lovelace"""

    # await update_hacs()
    await update_resources()
    await update_dashboards()


def lovelace_mode(config: ConfigType = {}) -> str:
    """Get the Lovelace mode from the configuration file."""

    return config.get(CONF_MODE, MODE_STORAGE)


async def update_hacs() -> None:
    """Install or update hacs integrations and frontend plugins."""

    base = get_base()
    hass = base.hass
    hacs = get_hacs()

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
                base.log.error("Unable to install HACS repository: %s", hacs_plugin)
        except:
            base.log.warning(
                f"Could not connect to HACS install '{hacs_plugin}', will assume everything is okay."
            )


async def add_resource_module(url: str) -> None:
    """Add a resource to the Lovelace resources list if it doesn't exist."""

    base = get_base()
    resources: Type[StorageCollection] = base.hass.data[LOVELACE_DOMAIN][CONF_RESOURCES]

    for resource in resources.async_items():
        if resource[CONF_URL] == url:
            # Item is already in the list
            return

    if base.configuration.lovelace_mode == MODE_STORAGE:
        await resources.async_create_item(
            {CONF_URL: url, CONF_RESOURCE_TYPE_WS: LOVELACE_RESOURCE_TYPE_MODULE}
        )
    else:
        base.log.error(
            f"{url} is not in the lovelace:resources list in the configuration.yaml"
        )
        base.configuration.missing_resources.append(url)


async def update_resources() -> None:
    """Check Lovelace resources and and resources that are missing if in storage mode."""

    base = get_base()
    hacs = get_hacs()

    # Reset missing resources
    missing_resources = base.configuration.missing_resources = []

    # Add the HACS plugins to the list
    for hacs_plugin in HACS_PLUGINS:
        try:
            repo = hacs.get_by_name(hacs_plugin)
            url = f"/hacsfiles/{hacs_plugin.split('/')[-1]}/{repo.data.file_name}"

            try:
                await add_resource_module(url)
            except:
                base.log.error(
                    f"Unable to add {hacs_plugin} the the Lovelace resource list.",
                    hacs_plugin,
                )
                missing_resources.append(url)
        except:
            base.log.warning(
                f"Could not connect to HACS to check repository for '{hacs_plugin}', will assume everything is okay."
            )

    # Add custom cards to the list
    for card in LOVELACE_CUSTOM_CARDS:
        url = (
            f"/local/{LOVELACE_DASHBOARD_URL_PATH}/{card['dirname']}/{card['filename']}"
        )
        await add_resource_module(url)


async def update_dashboards() -> None:
    """Add this integrations Lovelace dashboard."""

    hass = get_base().hass

    config = {
        CONF_MODE: MODE_YAML,
        CONF_TITLE: TITLE,
        CONF_ICON: LOVELACE_DASHBOARD_ICON,
        CONF_SHOW_IN_SIDEBAR: True,
        CONF_REQUIRE_ADMIN: False,
        CONF_FILENAME: os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                LOVELACE_DIR,
                LOVELACE_FILENAME_SOURCE,
            )
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
