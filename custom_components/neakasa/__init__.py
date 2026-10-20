"""Neakasa integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.const import Platform

from .api_manager import clear_shared_api
from .coordinator import NeakasaCoordinator
from .data import NeakasaConfigEntry, NeakasaData
from .device_claims import release_claims
from .migration import async_migrate_entry

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

__all__ = ["async_migrate_entry", "async_setup_entry", "async_unload_entry"]

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Neakasa Integration from a config entry."""
    entry = cast("NeakasaConfigEntry", config_entry)

    coordinator = NeakasaCoordinator(hass, config_entry)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = NeakasaData(coordinator=coordinator)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle config options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    entry = cast("NeakasaConfigEntry", config_entry)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator = entry.runtime_data.coordinator
        clear_shared_api(coordinator.username)
        release_claims(hass, entry.entry_id)

    return unload_ok
