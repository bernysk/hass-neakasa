"""Sensor for individual cat weight measurements."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import UnitOfMass

from ..entity import NeakasaEntity

if TYPE_CHECKING:
    from homeassistant.helpers.device_registry import DeviceInfo

    from ..coordinator import NeakasaCoordinator


class NeakasaCatWeightSensor(NeakasaEntity, SensorEntity):
    """Weight measurement for a specific cat."""

    _attr_translation_key = "cat_sensor"
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: NeakasaCoordinator,
        device_info: DeviceInfo,
        iot_id: str,
        cat_name: str,
        cat_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device_info, iot_id)
        self._cat_id = cat_id
        self._attr_translation_placeholders = {"name": cat_name}

    @property
    def unique_id(self) -> str:
        """Return the device ID suffixed with this cat's ID."""
        return f"{self._iot_id}-cat-{self._cat_id}"

    @property
    def _records(self) -> list[dict]:
        """Return this cat's records, newest first."""
        snap = self._snap
        if snap is None:
            return []
        records = [r for r in snap.record_list if r.get("cat_id") == self._cat_id]
        return sorted(records, key=lambda r: r.get("end_time") or 0, reverse=True)

    @property
    def native_value(self) -> float | None:
        """Return the most recent weight measurement, or None without one."""
        records = self._records
        if not records:
            return None
        return records[0].get("weight")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes for the cat."""
        records = self._records
        if not records:
            return {}
        last = records[0]
        return {
            "start_time": datetime.fromtimestamp(last["start_time"], tz=UTC),
            "end_time": datetime.fromtimestamp(last["end_time"], tz=UTC),
        }
