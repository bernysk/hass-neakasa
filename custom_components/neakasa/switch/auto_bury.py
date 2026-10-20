"""Switch for automatic burying."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaAutoBurySwitch(NeakasaEntity, SwitchEntity):
    """Toggle for automatic burying after use."""

    _attr_translation_key = "auto_bury"
    _attr_icon = "mdi:window-closed"

    @property
    def is_on(self) -> bool:
        """Return whether auto-bury is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return snap.auto_bury

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.set_property(self._iot_id, "auto_bury", 1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.set_property(self._iot_id, "auto_bury", 0)
