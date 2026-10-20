"""Make sure each Neakasa device is managed by a single config entry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.core import HomeAssistant

_CLAIMS_KEY = "device_claims"


def _claims(hass: HomeAssistant) -> dict[str, str]:
    """Return the iot_id → entry_id map of devices claimed in this run."""
    return hass.data.setdefault(DOMAIN, {}).setdefault(_CLAIMS_KEY, {})


def _registry_owners(hass: HomeAssistant, iot_id: str) -> set[str]:
    """Return the enabled Neakasa entries the device registry links *iot_id* to."""
    device = dr.async_get(hass).async_get_device(identifiers={(DOMAIN, iot_id)})
    if device is None:
        return set()
    owners = set()
    for entry_id in device.config_entries:
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is not None and entry.domain == DOMAIN and entry.disabled_by is None:
            owners.add(entry_id)
    return owners


def managed_elsewhere(hass: HomeAssistant, entry_id: str, iot_id: str) -> bool:
    """
    Return True if another entry manages *iot_id*; otherwise claim it for *entry_id*.

    Two accounts can see the same litter box (e.g. one shared from the other).
    An entry already linked to the device in the registry keeps it across
    restarts; a device no entry has registered yet goes to the first to see it.
    """
    claims = _claims(hass)
    owner = claims.get(iot_id)
    if owner is not None:
        return owner != entry_id

    registry_owners = _registry_owners(hass, iot_id)
    if registry_owners and entry_id not in registry_owners:
        return True

    claims[iot_id] = entry_id
    return False


def release_claims(hass: HomeAssistant, entry_id: str) -> None:
    """Drop every claim held by *entry_id*, e.g. when it unloads."""
    claims = _claims(hass)
    for iot_id in [i for i, owner in claims.items() if owner == entry_id]:
        del claims[iot_id]


def all_managed(hass: HomeAssistant, iot_ids: Iterable[str]) -> bool:
    """Return True if every device in *iot_ids* already belongs to an entry."""
    ids = list(iot_ids)
    return bool(ids) and all(_registry_owners(hass, iot_id) for iot_id in ids)
