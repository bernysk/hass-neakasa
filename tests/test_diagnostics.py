"""Tests for diagnostics support."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from custom_components.neakasa.diagnostics import (
    TO_REDACT,
    async_get_config_entry_diagnostics,
)


def test_to_redact_contains_credentials() -> None:
    assert CONF_USERNAME in TO_REDACT
    assert CONF_PASSWORD in TO_REDACT


def _make_entry() -> MagicMock:
    entry = MagicMock()
    entry.data = {CONF_USERNAME: "user@example.com", CONF_PASSWORD: "hunter2"}
    entry.title = "Neakasa (user@example.com)"
    entry.version = 2
    entry.domain = "neakasa"
    entry.options = {"scan_interval": 60}
    coordinator = MagicMock()
    coordinator.username = "user@example.com"
    coordinator.device_ids = ["iot-001"]
    coordinator.data = {}
    entry.runtime_data.coordinator = coordinator
    return entry


async def test_async_get_config_entry_diagnostics() -> None:
    entry = _make_entry()
    redacted = {
        CONF_USERNAME: "user@example.com",
        CONF_PASSWORD: "**REDACTED**",
    }
    with patch(
        "custom_components.neakasa.diagnostics.async_redact_data",
        return_value=redacted,
    ) as redact_mock:
        result = await async_get_config_entry_diagnostics(None, entry)

    redact_mock.assert_called_once()
    assert result["entry"]["title"] == "Neakasa (user@example.com)"
    assert result["entry"]["version"] == 2
    assert result["entry"]["domain"] == "neakasa"
    assert result["entry"]["data"][CONF_PASSWORD] == "**REDACTED**"
    assert result["entry"]["options"] == {"scan_interval": 60}
    assert result["coordinator"]["username"] == "user@example.com"
    assert result["coordinator"]["device_ids"] == ["iot-001"]
    assert result["coordinator"]["data_device_count"] == 0


async def test_async_get_config_entry_diagnostics_no_data() -> None:
    entry = _make_entry()
    entry.runtime_data.coordinator.data = None
    with patch(
        "custom_components.neakasa.diagnostics.async_redact_data",
        return_value={},
    ):
        result = await async_get_config_entry_diagnostics(None, entry)
    assert result["coordinator"]["data_device_count"] == 0

    entry.runtime_data.coordinator.data = {"iot-001": object()}
    with patch(
        "custom_components.neakasa.diagnostics.async_redact_data",
        return_value={},
    ):
        result = await async_get_config_entry_diagnostics(None, entry)
    assert result["coordinator"]["data_device_count"] == 1
