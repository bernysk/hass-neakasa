"""Binary sensor for waste bin full state."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity

from ..entity import NeakasaEntity


class NeakasaBinFullBinarySensor(NeakasaEntity, BinarySensorEntity):
    """Binary sensor indicating whether the waste bin is full."""

    _attr_translation_key = "bin_full"
    _attr_icon = "mdi:delete-empty"

    @property
    def is_on(self) -> bool:
        """Return whether the bin is full."""
        snap = self._snap
        if snap is None:
            return False
        return snap.bin_full
