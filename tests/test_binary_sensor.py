"""Tests for binary_sensor entities and platform setup."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.neakasa.binary_sensor import async_setup_entry
from custom_components.neakasa.binary_sensor.bin_full import (
    NeakasaBinFullBinarySensor,
)
from custom_components.neakasa.coordinator import NeakasaDeviceSnapshot

FAKE_SNAPSHOT = NeakasaDeviceSnapshot(
    iot_id="iot-001",
    device_name="T1 Plus",
    category_key="CatLitter",
    product_key="a1nNMMJkLqG",
    product_name="T1 Plus",
    bin_full=True,
    clean_cfg={},
    sand_level_state=0,
    sand_level_percent=0,
    bucket_status=0,
    room_of_bin=0,
    young_cat_mode=False,
    child_lock=False,
    auto_bury=False,
    auto_level=False,
    silent_mode=False,
    wifi_rssi=0,
    auto_force_init=False,
    b_intrpt_range_det=False,
    stay_time=0,
    last_use=0,
    cat_list=[],
    record_list=[],
)

FAKE_DEVICE_INFO = {"identifiers": {("neakasa", "iot-001")}}


def test_is_on_when_full() -> None:
    coord = MagicMock()
    coord.device_snapshot.return_value = FAKE_SNAPSHOT
    entity = NeakasaBinFullBinarySensor(coord, FAKE_DEVICE_INFO, "iot-001")
    entity.hass = MagicMock()
    assert entity.is_on is True
    assert entity.state == "on"
    assert entity.translation_key == "bin_full"
    assert entity.unique_id == "iot-001-bin_full"


def test_is_off_when_not_full() -> None:
    snap = NeakasaDeviceSnapshot(
        iot_id="iot-001",
        device_name="T1",
        category_key="CatLitter",
        product_key="pk",
        product_name="T1 Plus",
        bin_full=False,
        clean_cfg={},
        sand_level_state=0,
        sand_level_percent=0,
        bucket_status=0,
        room_of_bin=0,
        young_cat_mode=False,
        child_lock=False,
        auto_bury=False,
        auto_level=False,
        silent_mode=False,
        wifi_rssi=0,
        auto_force_init=False,
        b_intrpt_range_det=False,
        stay_time=0,
        last_use=0,
    )
    coord = MagicMock()
    coord.device_snapshot.return_value = snap
    entity = NeakasaBinFullBinarySensor(coord, FAKE_DEVICE_INFO, "iot-001")
    entity.hass = MagicMock()
    assert entity.is_on is False
    assert entity.state == "off"


def test_is_off_without_snapshot() -> None:
    coord = MagicMock()
    coord.device_snapshot.return_value = None
    entity = NeakasaBinFullBinarySensor(coord, FAKE_DEVICE_INFO, "iot-001")
    entity.hass = MagicMock()
    assert entity.is_on is False


def _fake_platform_data() -> MagicMock:
    """Fake EntityPlatform.platform_data so async_write_ha_state can run."""
    platform_data = MagicMock()
    platform_data.platform_name = "binary_sensor"
    platform_data.domain = "binary_sensor"
    platform_data.platform_translations = {}
    platform_data.component_translations = {}
    platform_data.object_id_platform_translations = {}
    platform_data.object_id_component_translations = {}
    return platform_data


async def test_lifecycle_methods(hass) -> None:
    """Test that the entity subscribes to and handles coordinator updates."""
    coord = MagicMock()
    coord.device_snapshot.return_value = FAKE_SNAPSHOT
    entity = NeakasaBinFullBinarySensor(coord, FAKE_DEVICE_INFO, "iot-001")
    entity.hass = hass
    entity.platform_data = _fake_platform_data()
    entity.entity_id = "binary_sensor.neakasa_bin_full"

    await entity.async_added_to_hass()
    assert coord.async_add_listener.called

    entity._handle_coordinator_update()


async def test_async_setup_entry(hass) -> None:
    """Test that setup registers a bin-full sensor per device."""
    from custom_components.neakasa.const import DOMAIN

    coordinator = MagicMock()
    coordinator.data = {"iot-001": FAKE_SNAPSHOT}
    coordinator.async_add_listener = MagicMock()

    config_entry = MagicMock()
    config_entry.runtime_data.coordinator = coordinator
    config_entry.async_on_unload = MagicMock()
    config_entry.domain = DOMAIN

    collected: list = []

    await async_setup_entry(hass, config_entry, collected.extend)

    assert len(collected) == 1
    assert isinstance(collected[0], NeakasaBinFullBinarySensor)
    assert config_entry.async_on_unload.called

    # A second discovery pass must not duplicate the entity
    rediscover = coordinator.async_add_listener.call_args.args[0]
    rediscover()
    assert len(collected) == 1
