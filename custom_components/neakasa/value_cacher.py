"""Time-based cache for slow cloud lookups."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


class ValueCacher:
    """Cache one value, refreshing it when stale and falling back to it on errors."""

    def __init__(
        self, refresh_after: timedelta | None, discard_after: timedelta | None
    ) -> None:
        self._refresh_after = refresh_after
        self._discard_after = discard_after
        self._manually_marked_stale = False
        self._value: Any | None = None
        self._last_update: datetime | None = None
        self._lock = asyncio.Lock()
        self._inflight: asyncio.Task[Any] | None = None

    def set(self, value: Any) -> None:
        self._value = value
        self._last_update = datetime.now(UTC)
        self._manually_marked_stale = False

    def clear(self) -> None:
        self._value = None
        self._last_update = None
        self._manually_marked_stale = False

    def mark_as_stale(self) -> None:
        self._manually_marked_stale = True

    def value_if_not_stale(self) -> Any | None:
        if (
            self._manually_marked_stale
            or self._value is None
            or self._last_update is None
        ):
            return None
        if self._refresh_after is not None:
            if self._refresh_after <= timedelta(0):
                return None
            if datetime.now(UTC) - self._last_update > self._refresh_after:
                return None
        return self._value

    def value_if_not_discarded(self) -> Any | None:
        if self._value is None or self._last_update is None:
            return None
        if self._discard_after is not None:
            if self._discard_after <= timedelta(0):
                return None
            if datetime.now(UTC) - self._last_update > self._discard_after:
                return None
        return self._value

    async def get_or_update(
        self, update_func: Callable[[], Coroutine[Any, Any, Any]]
    ) -> Any:
        # fast path
        current = self.value_if_not_stale()
        if current is not None:
            return current

        async with self._lock:
            # re-check under lock
            current = self.value_if_not_stale()
            if current is not None:
                return current

            if self._inflight is not None:
                try:
                    return await self._inflight
                except Exception:
                    fallback = self.value_if_not_discarded()
                    if fallback is not None:
                        return fallback
                    raise

            self._inflight = asyncio.get_running_loop().create_task(update_func())
            try:
                result = await self._inflight
                self.set(result)
                return result
            except Exception:
                fallback = self.value_if_not_discarded()
                if fallback is not None:
                    return fallback
                raise
            finally:
                self._inflight = None
