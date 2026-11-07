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
# Creating the per-account lock must itself be serialised, otherwise two
# concurrent first callers each get their own lock and both log in.
_registry_lock = asyncio.Lock()


def _account_key(username: str) -> str:
    """Key cached clients by account, never by the password."""
    return username.strip().lower()


async def _account_lock(account_key: str) -> asyncio.Lock:
    """Return the account's lock, creating it atomically on first use."""
    async with _registry_lock:
        return _shared_locks.setdefault(account_key, asyncio.Lock())


async def _connect_locked(
    hass: HomeAssistant, account_key: str, username: str, password: str
) -> NeakasaApiClient:
    """Log in and cache a new client; the caller holds the account lock."""
    session = async_get_clientsession(hass)
    client = NeakasaApiClient(NeakasaAPI(session))
    try:
        # Every login mints a new account session, which can sign the official
        # app out, so log each one to make session churn visible.
        _LOGGER.debug("Logging in to the Neakasa cloud (new account session)")
        await client.connect(username, password)
    except Exception:
        _LOGGER.error("Failed to log in to the Neakasa cloud", exc_info=True)
        raise
    _shared_clients[account_key] = client
    return client


async def get_shared_api(
    hass: HomeAssistant, username: str, password: str
) -> NeakasaApiClient:
    """Get or create the shared API client for the given account."""
    account_key = _account_key(username)
    async with await _account_lock(account_key):
        client = _shared_clients.get(account_key)
        if client is not None:
            if client.connected:
                return client
            _LOGGER.debug("Cached API client is disconnected, replacing it")
            del _shared_clients[account_key]
        return await _connect_locked(hass, account_key, username, password)


def peek_shared_api(username: str) -> NeakasaApiClient | None:
    """Return the cached client for the account, connected or not, or None."""
    return _shared_clients.get(_account_key(username))


def clear_shared_api(username: str) -> None:
    """
    Clear the shared API client for the given account.

    The account lock is kept, so callers waiting on it cannot start a second
    login alongside one that is already running.
    """
    _shared_clients.pop(_account_key(username), None)


async def force_reconnect_api(
    hass: HomeAssistant,
    username: str,
    password: str,
    stale: NeakasaApiClient | None = None,
) -> NeakasaApiClient:
    """
    Log in again and replace the shared client.

    With *stale* (the client a caller saw fail), a client that another caller
    already replaced it with is reused instead of logging in a second time.
    """
    account_key = _account_key(username)
    async with await _account_lock(account_key):
        current = _shared_clients.get(account_key)
        if (
            stale is not None
            and current is not None
            and current is not stale
            and current.connected
        ):
            _LOGGER.debug("Another caller already reconnected; reusing its client")
            return current
        _shared_clients.pop(account_key, None)
        return await _connect_locked(hass, account_key, username, password)
