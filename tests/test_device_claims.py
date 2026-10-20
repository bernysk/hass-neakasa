"""Tests for single-entry device ownership."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryDisabler
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.neakasa.const import DOMAIN
from custom_components.neakasa.device_claims import (
    all_managed,
    managed_elsewhere,
    release_claims,
)


def _entry(hass: HomeAssistant, name: str) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, version=2, unique_id=f"account:{name}")
    entry.add_to_hass(hass)
    return entry


def _register(hass: HomeAssistant, entry: MockConfigEntry, iot_id: str) -> None:
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={(DOMAIN, iot_id)}
    )


async def test_first_entry_to_see_a_new_device_claims_it(hass: HomeAssistant) -> None:
    first, second = _entry(hass, "a"), _entry(hass, "b")

    assert managed_elsewhere(hass, first.entry_id, "iot-1") is False
    assert managed_elsewhere(hass, second.entry_id, "iot-1") is True
    assert managed_elsewhere(hass, first.entry_id, "iot-1") is False


async def test_registry_owner_keeps_device_across_restarts(
    hass: HomeAssistant,
) -> None:
    owner, other = _entry(hass, "a"), _entry(hass, "b")
    _register(hass, owner, "iot-1")

    assert managed_elsewhere(hass, other.entry_id, "iot-1") is True
    assert managed_elsewhere(hass, owner.entry_id, "iot-1") is False


async def test_disabled_registry_owner_is_ignored(hass: HomeAssistant) -> None:
    owner, other = _entry(hass, "a"), _entry(hass, "b")
    _register(hass, owner, "iot-1")
    await hass.config_entries.async_set_disabled_by(
        owner.entry_id, ConfigEntryDisabler.USER
    )

    assert managed_elsewhere(hass, other.entry_id, "iot-1") is False


async def test_release_claims_hands_device_over(hass: HomeAssistant) -> None:
    first, second = _entry(hass, "a"), _entry(hass, "b")
    managed_elsewhere(hass, first.entry_id, "iot-1")

    release_claims(hass, first.entry_id)

    assert managed_elsewhere(hass, second.entry_id, "iot-1") is False


async def test_all_managed(hass: HomeAssistant) -> None:
    owner = _entry(hass, "a")
    _register(hass, owner, "iot-1")

    assert all_managed(hass, ["iot-1"]) is True
    assert all_managed(hass, ["iot-1", "iot-2"]) is False
    assert all_managed(hass, []) is False
