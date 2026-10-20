"""Tests for the NeakasaEntity base class."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.neakasa.switch.auto_bury import NeakasaAutoBurySwitch

FAKE_DEVICE_INFO = DeviceInfo(name="T1", manufacturer="Neakasa")


def _entity(snapshot: object, *, last_update_success: bool = True):
    coordinator = MagicMock()
    coordinator.last_update_success = last_update_success
    coordinator.device_snapshot.return_value = snapshot
    return NeakasaAutoBurySwitch(coordinator, FAKE_DEVICE_INFO, "iot-001")


def test_available_with_snapshot() -> None:
    assert _entity(MagicMock()).available is True


def test_unavailable_without_snapshot() -> None:
    assert _entity(None).available is False


def test_unavailable_when_update_failed() -> None:
    assert _entity(MagicMock(), last_update_success=False).available is False


def test_unique_id_and_device_info() -> None:
    entity = _entity(MagicMock())
    assert entity.unique_id == "iot-001-auto_bury"
    assert entity.device_info == FAKE_DEVICE_INFO
