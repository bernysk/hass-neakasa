"""Sensor for WiFi RSSI."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS, EntityCategory

from ..entity import NeakasaEntity


class NeakasaWifiRssiSensor(NeakasaEntity, SensorEntity):
    """WiFi signal strength in dBm."""

    _attr_translation_key = "wifi_rssi"
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:wifi"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the WiFi RSSI value."""
        snap = self._snap
        if snap is None:
            return None
        return snap.wifi_rssi
