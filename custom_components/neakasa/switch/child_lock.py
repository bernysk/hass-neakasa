"""Switch for child lock."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaChildLockSwitch(NeakasaEntity, SwitchEntity):
    """Toggle for the child lock."""

    _attr_translation_key = "child_lock"
    _attr_icon = "mdi:lock-alert"

    @property
    def is_on(self) -> bool:
        """Return whether child lock is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return snap.child_lock

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.set_property(self._iot_id, "child_lock", 1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.set_property(self._iot_id, "child_lock", 0)
