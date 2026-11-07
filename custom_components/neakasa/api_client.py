"""API client facade with translated error hierarchy."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from .api import APIAuthError, APIConnectionError, NeakasaAPI
from .exceptions import (
    NeakasaApiClientAuthenticationError,
    NeakasaApiClientCommunicationError,
    NeakasaApiClientSessionExpiredError,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


# The IoT gateway words a rejected session with "auth"/"session"/"expired";
# the account web API behind /catbox/record answers "TokenInvalid: token is
# abnormal". All of them mean the session is gone, not that the network failed.
_EXPIRED_TOKEN_PHRASES: tuple[str, ...] = (
    "session",
    "expired",
    "auth",
    "tokeninvalid",
    "token is abnormal",
)
# The web API token comes from the login response itself; renewing the IoT
# token cannot replace it, only a full login can.
_WEB_TOKEN_PHRASES: tuple[str, ...] = ("tokeninvalid", "token is abnormal")


def _is_expired_token(message: str, *, match_auth: bool = True) -> bool:
    """
    Return whether *message* words a rejected token or session.

    A login failure (``APIAuthError``) is checked without the bare ``auth``
    word, so a rejected password keeps reaching the reauth flow.
    """
    lowered = message.lower()
    phrases = (
        _EXPIRED_TOKEN_PHRASES
        if match_auth
        else tuple(p for p in _EXPIRED_TOKEN_PHRASES if p != "auth")
    )
    return any(phrase in lowered for phrase in phrases)


def needs_full_login(err: BaseException) -> bool:
    """Return whether *err* rejects the login token, which only a login renews."""
    lowered = str(err).lower()
    return any(phrase in lowered for phrase in _WEB_TOKEN_PHRASES)


@asynccontextmanager
async def _translate_errors() -> AsyncIterator[None]:
    """Map legacy API exceptions into the typed NeakasaApiClientError hierarchy."""
    try:
        yield
    except APIAuthError as err:
        message = str(err)
        if _is_expired_token(message, match_auth=False):
            _LOGGER.info(
                "Error translation: APIAuthError -> SessionExpired"
                " (matched a token/session phrase in: %r)",
                message,
            )
            raise NeakasaApiClientSessionExpiredError(message) from err
        _LOGGER.info(
            "Error translation: APIAuthError -> AuthenticationError"
            " (no token/session phrase in: %r)",
            message,
        )
        raise NeakasaApiClientAuthenticationError(message) from err
    except APIConnectionError as err:
        message = str(err)
        if _is_expired_token(message):
            _LOGGER.info(
                "Error translation: APIConnectionError -> SessionExpired"
                " (matched a token/session phrase in: %r)",
                message,
            )
            raise NeakasaApiClientSessionExpiredError(message) from err
        _LOGGER.info(
            "Error translation: APIConnectionError -> CommunicationError"
            " (no token/session phrase in: %r)",
            message,
        )
        raise NeakasaApiClientCommunicationError(message) from err


class NeakasaApiClient:
    """Thin facade around :class:`NeakasaAPI` that translates legacy errors."""

    def __init__(self, api: NeakasaAPI) -> None:
        """Wrap an authenticated *api* instance."""
        self._api = api

    @property
    def connected(self) -> bool:
        """Return whether the underlying API is authenticated."""
        return self._api.connected

    async def connect(self, username: str, password: str) -> None:
        """Authenticate, translating errors."""
        async with _translate_errors():
            await self._api.connect(username, password)

    async def refresh_session(self) -> None:
        """Renew the IoT token without a full login, translating errors."""
        async with _translate_errors():
            await self._api.refresh_session()

    async def get_devices(self, page_no: int = 1, page_size: int = 20) -> Any:
        """Fetch devices, translating errors."""
        async with _translate_errors():
            return await self._api.get_devices(page_no, page_size)

    async def get_device_properties(self, iot_id: str) -> Any:
        """Fetch device properties, translating errors."""
        async with _translate_errors():
            return await self._api.get_device_properties(iot_id)

    async def set_device_properties(self, iot_id: str, items: dict[str, Any]) -> None:
        """Set device properties, translating errors."""
        async with _translate_errors():
            await self._api.set_device_properties(iot_id, items)

    async def clean_now(self, iot_id: str) -> None:
        """Trigger an immediate clean cycle."""
        async with _translate_errors():
            await self._api.clean_now(iot_id)

    async def sand_leveling(self, iot_id: str) -> None:
        """Trigger an immediate sand-leveling cycle."""
        async with _translate_errors():
            await self._api.sand_leveling(iot_id)

    async def get_records(self, device_name: str, days: int = 7) -> Any:
        """Fetch toilet records, translating errors."""
        async with _translate_errors():
            return await self._api.get_records(device_name, days)

    async def get_statistics(self, device_name: str, days: int = 7) -> Any:
        """Fetch statistics, translating errors."""
        async with _translate_errors():
            return await self._api.get_statistics(device_name, days)
