"""Tests for ValueCacher."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from custom_components.neakasa.value_cacher import ValueCacher


def test_initial_state() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    assert cacher.value_if_not_stale() is None
    assert cacher.value_if_not_discarded() is None


def test_set_clear_and_stale() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    cacher.set("value")
    assert cacher.value_if_not_stale() == "value"
    assert cacher.value_if_not_discarded() == "value"

    cacher.mark_as_stale()
    assert cacher.value_if_not_stale() is None
    assert cacher.value_if_not_discarded() == "value"

    cacher.clear()
    assert cacher.value_if_not_stale() is None
    assert cacher.value_if_not_discarded() is None


def test_refresh_after_non_positive() -> None:
    cacher = ValueCacher(refresh_after=timedelta(0), discard_after=None)
    cacher.set(1)
    assert cacher.value_if_not_stale() is None


def test_refresh_after_expired() -> None:
    cacher = ValueCacher(refresh_after=timedelta(seconds=60), discard_after=None)
    cacher._value = 1
    cacher._last_update = datetime.now(UTC) - timedelta(minutes=5)
    assert cacher.value_if_not_stale() is None


def test_refresh_after_not_expired() -> None:
    cacher = ValueCacher(refresh_after=timedelta(seconds=60), discard_after=None)
    cacher.set(1)
    assert cacher.value_if_not_stale() == 1


def test_discard_after_non_positive() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=timedelta(0))
    cacher.set(1)
    assert cacher.value_if_not_discarded() is None


def test_discard_after_expired() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=timedelta(minutes=30))
    cacher._value = 1
    cacher._last_update = datetime.now(UTC) - timedelta(hours=1)
    assert cacher.value_if_not_discarded() is None


async def test_get_or_update_fast_path() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    cacher.set("cached")
    calls = 0

    async def update() -> str:
        nonlocal calls
        calls += 1
        return "fresh"

    assert await cacher.get_or_update(update) == "cached"
    assert calls == 0


async def test_get_or_update_misses_cache() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    calls = 0

    async def update() -> str:
        nonlocal calls
        calls += 1
        return "fresh"

    assert await cacher.get_or_update(update) == "fresh"
    assert calls == 1
    assert cacher.value_if_not_stale() == "fresh"


async def test_get_or_update_joins_inflight() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    loop = asyncio.get_running_loop()
    inflight = loop.create_future()
    inflight.set_result("done")
    cacher._inflight = inflight

    async def update() -> str:
        return "unused"

    assert await cacher.get_or_update(update) == "done"


async def test_get_or_update_inflight_error_uses_fallback() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    loop = asyncio.get_running_loop()
    inflight = loop.create_future()
    inflight.set_exception(RuntimeError("boom"))
    cacher._inflight = inflight
    cacher.set("fallback")
    cacher.mark_as_stale()

    async def update() -> str:
        return "unused"

    assert await cacher.get_or_update(update) == "fallback"


async def test_get_or_update_inflight_error_raises() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    loop = asyncio.get_running_loop()
    inflight = loop.create_future()
    inflight.set_exception(RuntimeError("boom"))
    cacher._inflight = inflight

    async def update() -> str:
        return "unused"

    with pytest.raises(RuntimeError):
        await cacher.get_or_update(update)


async def test_get_or_update_update_error_raises() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)

    async def update() -> str:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await cacher.get_or_update(update)
    assert cacher._inflight is None


async def test_get_or_update_update_error_uses_fallback() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    cacher.set("fallback")
    cacher.mark_as_stale()

    async def update() -> str:
        raise RuntimeError("boom")

    assert await cacher.get_or_update(update) == "fallback"


async def test_get_or_update_second_caller_hits_cache() -> None:
    cacher = ValueCacher(refresh_after=None, discard_after=None)
    calls = 0
    entered = asyncio.Event()
    t2_started = asyncio.Event()

    async def update() -> str:
        nonlocal calls
        calls += 1
        entered.set()
        await t2_started.wait()
        return "fresh"

    async def first() -> str:
        return await cacher.get_or_update(update)

    async def second() -> str:
        t2_started.set()
        return await cacher.get_or_update(update)

    t1 = asyncio.create_task(first())
    await entered.wait()
    t2 = asyncio.create_task(second())
    results = await asyncio.gather(t1, t2)
    assert results == ["fresh", "fresh"]
    assert calls == 1
