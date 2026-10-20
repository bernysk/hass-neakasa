"""Switch for automatic recovery after power loss."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaAutoRecoverySwitch(NeakasaEntity, SwitchEntity):
    """Toggle for automatic recovery after power loss."""

    _attr_translation_key = "auto_recovery"
    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:alert-outline"

    @property
    def is_on(self) -> bool:
        """Return whether auto-recovery is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return snap.auto_force_init

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.set_property(self._iot_id, "auto_force_init", 1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.set_property(self._iot_id, "auto_force_init", 0)
