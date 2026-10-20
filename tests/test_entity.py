"""Tests for the NeakasaEntity base class."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.neakasa.const import DOMAIN
from custom_components.neakasa.entity import neakasa_device_info
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


def test_device_info_includes_model() -> None:
    snap = MagicMock(
        iot_id="iot-001", device_name="T1", product_name="M1", product_key="pk1"
    )
    info = neakasa_device_info(snap)
    assert info["identifiers"] == {(DOMAIN, "iot-001")}
    assert info["model"] == "M1"
    assert info["model_id"] == "pk1"


def test_device_info_without_model() -> None:
    snap = MagicMock(
        iot_id="iot-001", device_name="T1", product_name="", product_key=""
    )
    info = neakasa_device_info(snap)
    assert info["model"] is None
    assert info["model_id"] is None
