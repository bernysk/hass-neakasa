"""Switch for unstoppable cleaning cycle."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaUnstoppableCycleSwitch(NeakasaEntity, SwitchEntity):
    """Toggle for unstoppable cleaning cycle (interrupt range detection)."""

    _attr_translation_key = "unstoppable_cycle"
    _attr_icon = "mdi:cached"

    @property
    def is_on(self) -> bool:
        """Return whether unstoppable cycle is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return snap.b_intrpt_range_det

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.set_property(self._iot_id, "b_intrpt_range_det", 1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.set_property(self._iot_id, "b_intrpt_range_det", 0)
