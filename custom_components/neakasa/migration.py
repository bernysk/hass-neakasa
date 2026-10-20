"""Config entry migrations for Neakasa."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import _LOGGER, CONFIG_MINOR_VERSION, CONFIG_VERSION, DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


def _account_owner(hass: HomeAssistant, config_entry: ConfigEntry) -> ConfigEntry:
    """Return the entry that owns *config_entry*'s account: the first one listed."""
    username = config_entry.data[CONF_USERNAME].lower()
    return next(
        (
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if entry.data.get(CONF_USERNAME, "").lower() == username
        ),
        config_entry,
    )


def _move_registry_entries(
    hass: HomeAssistant, source: ConfigEntry, target: ConfigEntry
) -> None:
    """Reassign *source*'s devices and entities to *target* so removal keeps them."""
    entity_registry = er.async_get(hass)
    for entity in er.async_entries_for_config_entry(entity_registry, source.entry_id):
        entity_registry.async_update_entity(
            entity.entity_id, config_entry_id=target.entry_id
        )
    device_registry = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(device_registry, source.entry_id):
        device_registry.async_update_device(
            device.id,
            add_config_entry_id=target.entry_id,
            remove_config_entry_id=source.entry_id,
        )


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """
    Migrate a config entry to version 2.2.

    V1 stored one entry per device, keyed by the device IOT ID. V2 keeps one
    entry per account (``account:{username}``) that sets up every device, so
    accounts with several V1 entries are collapsed into the first one; V2.2
    also cleans up duplicates left behind by the original V1 → V2 migration.
    """
    if config_entry.version > CONFIG_VERSION:
        return False

    username = config_entry.data[CONF_USERNAME]
    owner = _account_owner(hass, config_entry)
    if owner.entry_id != config_entry.entry_id:
        _LOGGER.info(
            "Removing duplicate config entry %s; entry %s already covers the account",
            config_entry.entry_id,
            owner.entry_id,
        )
        _move_registry_entries(hass, config_entry, owner)
        hass.async_create_task(hass.config_entries.async_remove(config_entry.entry_id))
        return False

    if config_entry.version == 1:
        _LOGGER.debug("Migrating config entry %s from V1 to V2", config_entry.entry_id)
        hass.config_entries.async_update_entry(
            config_entry,
            data={
                CONF_USERNAME: username,
                CONF_PASSWORD: config_entry.data[CONF_PASSWORD],
            },
            unique_id=f"account:{username.lower()}",
            version=CONFIG_VERSION,
            minor_version=CONFIG_MINOR_VERSION,
        )
    elif config_entry.minor_version < CONFIG_MINOR_VERSION:
        hass.config_entries.async_update_entry(
            config_entry, minor_version=CONFIG_MINOR_VERSION
        )
    return True
