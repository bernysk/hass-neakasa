"""Switch to toggle auto-clean scheduling."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaAutoCleanSwitch(NeakasaEntity, SwitchEntity):
    """Toggle for the auto-clean schedule."""

    _attr_translation_key = "auto_clean"
    _attr_icon = "mdi:vacuum"

    @property
    def is_on(self) -> bool:
        """Return whether auto-clean is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return bool(snap.clean_cfg.get("active", False))

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self._set_active(1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self._set_active(0)

    async def _set_active(self, value: int) -> None:
        snap = self._snap
        if snap is None:
            return
        cfg = dict(snap.clean_cfg)
        cfg["active"] = value
        await self.coordinator.set_property(self._iot_id, "clean_cfg", cfg)
