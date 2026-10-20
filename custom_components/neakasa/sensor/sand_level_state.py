"""Sensor for the cat litter fill state."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

from ..entity import NeakasaEntity

_LEVEL_OPTIONS = ["insufficient", "moderate", "sufficient", "overfilled"]


class NeakasaSandLevelStateSensor(NeakasaEntity, SensorEntity):
    """Cat litter fill state (insufficient, moderate, sufficient, overfilled)."""

    _attr_translation_key = "sand_state"

    @property
    def native_value(self) -> str | int | None:
        """Return the mapped sand level."""
        snap = self._snap
        if snap is None:
            return None
        raw = snap.sand_level_state
        if raw >= len(_LEVEL_OPTIONS):
            return raw
        value = _LEVEL_OPTIONS[raw]
        return raw if value is None else value
