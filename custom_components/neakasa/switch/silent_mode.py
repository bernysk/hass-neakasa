"""Switch for silent mode."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaSilentModeSwitch(NeakasaEntity, SwitchEntity):
    """Toggle for silent mode."""

    _attr_translation_key = "silent_mode"
    _attr_icon = "mdi:volume-off"

    @property
    def is_on(self) -> bool:
        """Return whether silent mode is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return snap.silent_mode

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.set_property(self._iot_id, "silent_mode", 1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.set_property(self._iot_id, "silent_mode", 0)
