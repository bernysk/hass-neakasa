"""Button to trigger an immediate clean cycle."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from ..entity import NeakasaEntity


class NeakasaCleanButton(NeakasaEntity, ButtonEntity):
    """Button to start an immediate cleaning cycle."""

    _attr_translation_key = "clean"

    async def async_press(self) -> None:
        """Trigger a clean cycle."""
        await self.coordinator.invoke_service(self._iot_id, "clean")
