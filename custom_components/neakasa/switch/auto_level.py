"""Switch for automatic sand leveling."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaAutoLevelSwitch(NeakasaEntity, SwitchEntity):
    """Toggle for automatic sand leveling."""

    _attr_translation_key = "auto_level"
    _attr_icon = "mdi:spirit-level"

    @property
    def is_on(self) -> bool:
        """Return whether auto-level is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return snap.auto_level

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.set_property(self._iot_id, "auto_level", 1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.set_property(self._iot_id, "auto_level", 0)
