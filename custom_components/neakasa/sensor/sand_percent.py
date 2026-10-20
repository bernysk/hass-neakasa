"""Sensor for cat litter fill percentage."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE

from ..entity import NeakasaEntity


class NeakasaSandPercentSensor(NeakasaEntity, SensorEntity):
    """Cat litter fill level as a percentage."""

    _attr_translation_key = "sand_percent"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the sand level percentage."""
        snap = self._snap
        if snap is None:
            return None
        return snap.sand_level_percent
