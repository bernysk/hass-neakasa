"""Tests for __init__.py — integration setup/teardown."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from custom_components.neakasa import (
    PLATFORMS,
    _async_update_listener,
    async_migrate_entry,
    async_setup_entry,
    async_unload_entry,
)


async def test_platforms_present() -> None:
    """Verify we register all expected platforms."""
    for platform_name in ("sensor", "binary_sensor", "switch", "button"):
        assert any(p.value == platform_name for p in PLATFORMS), (
            f"Missing platform: {platform_name}"
        )


async def test_async_setup_entry(
    hass: HomeAssistant,
    mock_config_entry: MagicMock,
    mock_get_shared_api: MagicMock,
) -> None:
    """Test that setup_entry creates coordinator and forwards platforms."""
    with (
        patch(
            "custom_components.neakasa.NeakasaCoordinator",
            autospec=True,
        ) as mock_coord_cls,
        patch.object(hass.config_entries, "async_forward_entry_setups") as fwd,
    ):
        mock_coordinator = mock_coord_cls.return_value
        mock_coordinator.async_config_entry_first_refresh.return_value = None

        result = await async_setup_entry(hass, mock_config_entry)
        assert result is True
        mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()
        fwd.assert_awaited_once()


async def test_async_setup_entry_assigns_runtime_data(
    hass: HomeAssistant,
    mock_config_entry: MagicMock,
    mock_get_shared_api: MagicMock,
) -> None:
    """Test that setup_entry stores coordinator in runtime_data."""
    mock_config_entry.runtime_data = MagicMock()
    with (
        patch(
            "custom_components.neakasa.NeakasaCoordinator",
            autospec=True,
        ) as mock_coord_cls,
        patch.object(hass.config_entries, "async_forward_entry_setups"),
    ):
        mock_coordinator = mock_coord_cls.return_value
        mock_coordinator.async_config_entry_first_refresh.return_value = None

        await async_setup_entry(hass, mock_config_entry)
        assert mock_config_entry.runtime_data.coordinator is mock_coordinator
        mock_config_entry.add_update_listener.assert_called_once_with(
            _async_update_listener
        )
        assert mock_config_entry.async_on_unload.called


async def test_async_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MagicMock,
) -> None:
    """Test that unload_entry unloads platforms and clears shared API."""
    with (
        patch.object(
            hass.config_entries, "async_unload_platforms", return_value=True
        ) as unload,
        patch("custom_components.neakasa.clear_shared_api") as clear_api,
    ):
        result = await async_unload_entry(hass, mock_config_entry)
        assert result is True
        unload.assert_awaited_once()
        clear_api.assert_called_once()


async def test_async_migrate_entry_v1() -> None:
    """Test migrating a V1 config entry to V2."""
    hass = MagicMock()
    hass.config_entries.async_update_entry = MagicMock()
    entry = MagicMock()
    entry.version = 1
    entry.entry_id = "entry-1"
    entry.data = {
        CONF_USERNAME: "User@Example.com",
        CONF_PASSWORD: "hunter2",
    }

    result = await async_migrate_entry(hass, entry)

    assert result is True
    hass.config_entries.async_update_entry.assert_called_once()
    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert call_kwargs["data"] == {
        CONF_USERNAME: "User@Example.com",
        CONF_PASSWORD: "hunter2",
    }
    assert call_kwargs["unique_id"] == "account:user@example.com"
    assert call_kwargs["version"] == 2


async def test_async_migrate_entry_v2_already() -> None:
    """Test that V2 entries are left untouched."""
    hass = MagicMock()
    hass.config_entries.async_update_entry = MagicMock()
    entry = MagicMock()
    entry.version = 2

    result = await async_migrate_entry(hass, entry)

    assert result is True
    hass.config_entries.async_update_entry.assert_not_called()


async def test_update_listener_reloads_entry() -> None:
    """Test that the update listener reloads the config entry."""
    hass = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    entry = MagicMock()
    entry.entry_id = "entry-1"

    await _async_update_listener(hass, entry)

    hass.config_entries.async_reload.assert_awaited_once_with("entry-1")
