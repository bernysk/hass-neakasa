"""Sensor for last cat stay duration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime

from ..entity import NeakasaEntity


class NeakasaStayTimeSensor(NeakasaEntity, SensorEntity):
    """Duration of the last cat visit in seconds."""

    _attr_translation_key = "stay_time"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_entity_registry_enabled_default = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the stay time in seconds."""
        snap = self._snap
        if snap is None:
            return None
        return snap.stay_time
