"""File operations for this integration."""
import shutil
import os

from homeassistant.core import HomeAssistant

from .const import (
    LOVELACE_CARD_DIR,
    LOVELACE_CUSTOM_CARDS,
    LOVELACE_DASHBOARD_URL_PATH,
    LOVELACE_DIR,
)


async def setup_files(hass) -> None:
    """Setup files for this integration."""
    await update_files(hass)


def mkdir(path: str, remove: bool = False) -> None:
    """Make a directory if it does not exist."""

    if os.path.exists(path) and remove:
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)


async def update_files(hass: HomeAssistant) -> None:
    """Copy files from the integration's source to HA config directory."""
    py_dir = os.path.dirname(__file__)

    # Copy custom Lovelace cards
    local_dir = hass.config.path("www")
    mkdir(local_dir)
    card_dir = os.path.join(local_dir, LOVELACE_DASHBOARD_URL_PATH)
    mkdir(card_dir, True)
    for card in LOVELACE_CUSTOM_CARDS:
        src_card_dir = os.path.join(
            py_dir, LOVELACE_DIR, LOVELACE_CARD_DIR, card["dirname"]
        )
        dst_card_dir = os.path.join(card_dir, card["dirname"])
        shutil.copytree(src_card_dir, dst_card_dir)
