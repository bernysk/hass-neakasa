"""Button to trigger an immediate sand leveling."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from ..entity import NeakasaEntity


class NeakasaLevelButton(NeakasaEntity, ButtonEntity):
    """Button to start an immediate sand-leveling cycle."""

    _attr_translation_key = "level"

    async def async_press(self) -> None:
        """Trigger a sand-leveling cycle."""
        await self.coordinator.invoke_service(self._iot_id, "level")
