"""Tests for config entry migrations."""

from __future__ import annotations

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.neakasa.const import DOMAIN
from custom_components.neakasa.migration import async_migrate_entry


def _entry(
    hass: HomeAssistant,
    *,
    username: str = "User@Example.com",
    unique_id: str = "iot-001",
    version: int = 1,
    minor_version: int = 1,
) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=version,
        minor_version=minor_version,
        unique_id=unique_id,
        data={
            CONF_USERNAME: username,
            CONF_PASSWORD: "hunter2",
            "device_id": unique_id,
            "friendly_name": "Litter box",
        },
    )
    entry.add_to_hass(hass)
    return entry


async def test_migrate_v1_single_entry(hass: HomeAssistant) -> None:
    entry = _entry(hass)

    assert await async_migrate_entry(hass, entry) is True

    assert entry.version == 2
    assert entry.minor_version == 2
    assert entry.unique_id == "account:user@example.com"
    assert entry.data == {CONF_USERNAME: "User@Example.com", CONF_PASSWORD: "hunter2"}


async def test_migrate_v1_collapses_entries_of_one_account(
    hass: HomeAssistant,
) -> None:
    first = _entry(hass, unique_id="iot-001")
    second = _entry(hass, username="user@example.com", unique_id="iot-002")
    other_account = _entry(hass, username="other@example.com", unique_id="iot-003")

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=second.entry_id, identifiers={(DOMAIN, "iot-002")}
    )
    entity_registry = er.async_get(hass)
    entity = entity_registry.async_get_or_create(
        "switch",
        DOMAIN,
        "iot-002-auto_bury",
        config_entry=second,
        device_id=device.id,
    )

    assert await async_migrate_entry(hass, second) is False
    await hass.async_block_till_done()
    assert await async_migrate_entry(hass, first) is True
    assert await async_migrate_entry(hass, other_account) is True

    entries = hass.config_entries.async_entries(DOMAIN)
    assert {e.entry_id for e in entries} == {first.entry_id, other_account.entry_id}
    assert entity_registry.async_get(entity.entity_id).config_entry_id == (
        first.entry_id
    )
    assert device_registry.async_get(device.id).config_entries == {first.entry_id}


async def test_migrate_v2_removes_leftover_duplicate(hass: HomeAssistant) -> None:
    kept = _entry(hass, unique_id="account:user@example.com", version=2)
    duplicate = _entry(hass, unique_id="account:user@example.com", version=2)

    assert await async_migrate_entry(hass, kept) is True
    assert kept.minor_version == 2
    assert await async_migrate_entry(hass, duplicate) is False
    await hass.async_block_till_done()

    assert [e.entry_id for e in hass.config_entries.async_entries(DOMAIN)] == [
        kept.entry_id
    ]


async def test_migrate_current_entry_untouched(hass: HomeAssistant) -> None:
    entry = _entry(
        hass, unique_id="account:user@example.com", version=2, minor_version=2
    )

    assert await async_migrate_entry(hass, entry) is True
    assert entry.unique_id == "account:user@example.com"


async def test_migrate_from_future_version_fails(hass: HomeAssistant) -> None:
    entry = _entry(hass, version=3)

    assert await async_migrate_entry(hass, entry) is False
