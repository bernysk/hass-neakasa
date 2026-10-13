"""Tests for the shared API client manager."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.neakasa.api_manager import (
    clear_shared_api,
    force_reconnect_api,
    get_shared_api,
)

USER = "user@example.com"
PASSWORD = "hunter2"


@pytest.fixture(autouse=True)
def _clean_shared_state() -> None:
    clear_shared_api(USER, PASSWORD)
    yield
    clear_shared_api(USER, PASSWORD)


def _patched_manager() -> tuple[MagicMock, MagicMock, MagicMock]:
    session = MagicMock()
    api_cls = MagicMock()
    client_cls = MagicMock()
    api_cls.return_value.connect = AsyncMock()
    client_cls.return_value.connected = True
    return session, api_cls, client_cls


async def test_get_shared_api_creates_client() -> None:
    session, api_cls, client_cls = _patched_manager()
    with (
        patch(
            "custom_components.neakasa.api_manager.async_get_clientsession",
            return_value=session,
        ),
        patch("custom_components.neakasa.api_manager.NeakasaAPI", api_cls),
        patch(
            "custom_components.neakasa.api_manager.NeakasaApiClient",
            client_cls,
        ),
    ):
        result = await get_shared_api(MagicMock(), USER, PASSWORD)
        assert result is client_cls.return_value
        api_cls.assert_called_once()
        api_cls.return_value.connect.assert_awaited_once_with(USER, PASSWORD)


async def test_get_shared_api_reuses_connected_client() -> None:
    session, api_cls, client_cls = _patched_manager()
    with (
        patch(
            "custom_components.neakasa.api_manager.async_get_clientsession",
            return_value=session,
        ),
        patch("custom_components.neakasa.api_manager.NeakasaAPI", api_cls),
        patch(
            "custom_components.neakasa.api_manager.NeakasaApiClient",
            client_cls,
        ),
    ):
        first = await get_shared_api(MagicMock(), USER, PASSWORD)
        second = await get_shared_api(MagicMock(), USER, PASSWORD)
        assert first is second
        api_cls.return_value.connect.assert_awaited_once()


async def test_get_shared_api_clears_invalid_client() -> None:
    session, api_cls, client_cls = _patched_manager()
    with (
        patch(
            "custom_components.neakasa.api_manager.async_get_clientsession",
            return_value=session,
        ),
        patch("custom_components.neakasa.api_manager.NeakasaAPI", api_cls),
        patch(
            "custom_components.neakasa.api_manager.NeakasaApiClient",
            client_cls,
        ),
    ):
        await get_shared_api(MagicMock(), USER, PASSWORD)
        client_cls.return_value.connected = False
        result = await get_shared_api(MagicMock(), USER, PASSWORD)
        assert result is client_cls.return_value
        assert api_cls.return_value.connect.await_count == 2


async def test_get_shared_api_auth_failure_raises() -> None:
    session, api_cls, client_cls = _patched_manager()
    api_cls.return_value.connect = AsyncMock(side_effect=RuntimeError("boom"))
    with (
        patch(
            "custom_components.neakasa.api_manager.async_get_clientsession",
            return_value=session,
        ),
        patch("custom_components.neakasa.api_manager.NeakasaAPI", api_cls),
        patch(
            "custom_components.neakasa.api_manager.NeakasaApiClient",
            client_cls,
        ),
        pytest.raises(RuntimeError),
    ):
        await get_shared_api(MagicMock(), USER, PASSWORD)


async def test_force_reconnect_api() -> None:
    session, api_cls, client_cls = _patched_manager()
    with (
        patch(
            "custom_components.neakasa.api_manager.async_get_clientsession",
            return_value=session,
        ),
        patch("custom_components.neakasa.api_manager.NeakasaAPI", api_cls),
        patch(
            "custom_components.neakasa.api_manager.NeakasaApiClient",
            client_cls,
        ),
    ):
        first = await get_shared_api(MagicMock(), USER, PASSWORD)
        second = await force_reconnect_api(MagicMock(), USER, PASSWORD)
        assert first is second
        assert api_cls.return_value.connect.await_count == 2
