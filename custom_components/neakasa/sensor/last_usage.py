"""Sensor for the timestamp of the last cat usage."""

from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from ..entity import NeakasaEntity


class NeakasaLastUsageSensor(NeakasaEntity, SensorEntity):
    """Timestamp of the last time a cat used the litter box."""

    _attr_translation_key = "last_usage"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the last-use timestamp."""
        snap = self._snap
        if snap is None:
            return None
        raw = snap.last_use
        if not raw:
            return None
        try:
            return datetime.fromtimestamp(raw / 1000, tz=UTC)
        except (TypeError, ValueError):
            return None
