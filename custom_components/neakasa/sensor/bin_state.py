"""Sensor for the waste bin state."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

from ..entity import NeakasaEntity

_BIN_OPTIONS = ["normal", "full", "missing"]


class NeakasaBinStateSensor(NeakasaEntity, SensorEntity):
    """Waste bin state (normal, full, missing)."""

    _attr_translation_key = "bin_state"
    _attr_icon = "mdi:delete"

    @property
    def native_value(self) -> str | int | None:
        """Return the mapped bin state."""
        snap = self._snap
        if snap is None:
            return None
        raw = snap.room_of_bin
        if raw >= len(_BIN_OPTIONS):
            return raw
        value = _BIN_OPTIONS[raw]
        return raw if value is None else value
