"""Base entity shared by all Neakasa platforms."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NeakasaCoordinator, NeakasaDeviceSnapshot


def neakasa_device_info(snap: NeakasaDeviceSnapshot) -> DeviceInfo:
    """Build the device registry entry for the device behind *snap*."""
    return DeviceInfo(
        identifiers={(DOMAIN, snap.iot_id)},
        name=snap.device_name,
        manufacturer="Neakasa",
        model=snap.product_name or None,
        model_id=snap.product_key or None,
    )


class NeakasaEntity(CoordinatorEntity[NeakasaCoordinator]):
    """Entity bound to a single Neakasa device of the coordinator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NeakasaCoordinator,
        device_info: DeviceInfo,
        iot_id: str,
    ) -> None:
        """Bind the entity to the device identified by *iot_id*."""
        super().__init__(coordinator)
        self._iot_id = iot_id
        self._attr_device_info = device_info

    @property
    def unique_id(self) -> str:
        """Return the device ID suffixed with the entity's translation key."""
        return f"{self._iot_id}-{self.translation_key}"

    @property
    def available(self) -> bool:
        """Return False when the last update had no data for this device."""
        return super().available and self._snap is not None

    @property
    def _snap(self) -> NeakasaDeviceSnapshot | None:
        return self.coordinator.device_snapshot(self._iot_id)
