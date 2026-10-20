"""Sensor for the device operational status."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

from ..entity import NeakasaEntity

_STATUS_OPTIONS = [
    "idle",
    "cleaning",
    "cleaning",
    "leveling",
    "flipover",
    "cat_present",
    "paused",
    "side_bin_locking_panels_missing",
    None,
    "cleaning_interrupted",
]


class NeakasaBucketStatusSensor(NeakasaEntity, SensorEntity):
    """Current device operational status (idle, cleaning, etc.)."""

    _attr_translation_key = "current_status"
    _attr_icon = "mdi:state-machine"

    @property
    def native_value(self) -> str | int | None:
        """Return the mapped status string."""
        snap = self._snap
        if snap is None:
            return None
        raw = snap.bucket_status
        if raw >= len(_STATUS_OPTIONS):
            return raw
        value = _STATUS_OPTIONS[raw]
        return raw if value is None else value
