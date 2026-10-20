"""Shared API client manager — extracted from __init__.py to avoid circular imports."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NeakasaAPI
from .api_client import NeakasaApiClient
from .const import _LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_shared_clients: dict[str, NeakasaApiClient] = {}
_shared_locks: dict[str, asyncio.Lock] = {}


def _account_key(username: str) -> str:
    """Key cached clients by account, never by the password."""
    return username.strip().lower()


async def get_shared_api(
    hass: HomeAssistant, username: str, password: str
) -> NeakasaApiClient:
    """Get or create a shared API client for the given credentials."""
    account_key = _account_key(username)
    if account_key not in _shared_locks:
        _shared_locks[account_key] = asyncio.Lock()
    async with _shared_locks[account_key]:
        if account_key in _shared_clients:
            client = _shared_clients[account_key]
            if client.connected:
                _LOGGER.debug("Reusing shared API client for %s", username)
                return client
            _LOGGER.debug("Clearing invalid API client for %s", username)
            del _shared_clients[account_key]

        session = async_get_clientsession(hass)
        client = NeakasaApiClient(NeakasaAPI(session))
        try:
            _LOGGER.debug("Authenticating shared API client for %s", username)
            await client.connect(username, password)
            _shared_clients[account_key] = client
            _LOGGER.debug("Authenticated shared API client for %s", username)
        except Exception:
            _LOGGER.error(
                "Failed to authenticate shared API for %s", username, exc_info=True
            )
            raise
        else:
            return client


def clear_shared_api(username: str) -> None:
    """Clear the shared API client for the given account."""
    account_key = _account_key(username)
    _shared_clients.pop(account_key, None)
    _shared_locks.pop(account_key, None)


async def force_reconnect_api(
    hass: HomeAssistant, username: str, password: str
) -> NeakasaApiClient:
    """Force reconnection of the API client for the given credentials."""
    _shared_clients.pop(_account_key(username), None)
    return await get_shared_api(hass, username, password)
