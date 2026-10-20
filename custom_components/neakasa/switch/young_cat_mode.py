"""Switch for kitten/young-cat mode."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from ..entity import NeakasaEntity


class NeakasaYoungCatModeSwitch(NeakasaEntity, SwitchEntity):
    """Toggle for kitten (young cat) mode."""

    _attr_translation_key = "young_cat_mode"
    _attr_entity_registry_enabled_default = False
    _attr_icon = "mdi:cat"

    @property
    def is_on(self) -> bool:
        """Return whether young cat mode is enabled."""
        snap = self._snap
        if snap is None:
            return False
        return snap.young_cat_mode

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.set_property(self._iot_id, "young_cat_mode", 1)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.set_property(self._iot_id, "young_cat_mode", 0)
