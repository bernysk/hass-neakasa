"""Tests for config_flow.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.neakasa.const import DOMAIN

FAKE_USERNAME = "test@example.com"
FAKE_PASSWORD = "hunter2"

FAKE_DEVICES = [
    {
        "iotId": "iot-001",
        "deviceName": "T1 Plus",
        "categoryKey": "CatLitter",
    }
]


async def test_flow_show_form(hass: HomeAssistant) -> None:
    """Test that the user step shows the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_flow_success(
    hass: HomeAssistant,
    mock_get_shared_api: MagicMock,
) -> None:
    """Test successful config flow creates entry."""
    with (
        patch(
            "custom_components.neakasa.config_flow.NeakasaAPI",
            autospec=True,
        ) as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient",
        ) as mock_client_cls,
    ):
        mock_api = mock_api_cls.return_value
        mock_api.connect = AsyncMock()

        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(return_value=FAKE_DEVICES)

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert result["type"] is FlowResultType.FORM

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: FAKE_USERNAME, CONF_PASSWORD: FAKE_PASSWORD},
        )
        assert result2["type"] is FlowResultType.CREATE_ENTRY
        assert result2["title"] == f"Neakasa ({FAKE_USERNAME})"


async def test_flow_abort_duplicate(
    hass: HomeAssistant,
    mock_get_shared_api: MagicMock,
) -> None:
    """Test that a duplicate config entry is aborted."""
    # Create a first entry so the second one gets aborted
    with (
        patch(
            "custom_components.neakasa.config_flow.NeakasaAPI",
            autospec=True,
        ) as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient",
        ) as mock_client_cls,
    ):
        mock_api = mock_api_cls.return_value
        mock_api.connect = AsyncMock()

        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(return_value=FAKE_DEVICES)

        # First flow: create entry
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: FAKE_USERNAME, CONF_PASSWORD: FAKE_PASSWORD},
        )
        assert result2["type"] is FlowResultType.CREATE_ENTRY

        # Second flow: should abort as duplicate
        result3 = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result4 = await hass.config_entries.flow.async_configure(
            result3["flow_id"],
            {CONF_USERNAME: FAKE_USERNAME, CONF_PASSWORD: FAKE_PASSWORD},
        )
        assert result4["type"] is FlowResultType.ABORT


async def test_reauth_flow() -> None:
    """Test that the config flow handler has reauth support."""
    from custom_components.neakasa.config_flow import NeakasaConfigFlow

    # Verify the flow handler defines the reauth step
    assert hasattr(NeakasaConfigFlow, "async_step_reauth")
    assert hasattr(NeakasaConfigFlow, "async_step_reauth_confirm")


# ---------------------------------------------------------------------------
# _validate_credentials unit tests
# ---------------------------------------------------------------------------


async def test_validate_credentials_success(hass: HomeAssistant) -> None:
    """Test that valid credentials return a client and no error."""
    from custom_components.neakasa.config_flow import _validate_credentials

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(return_value=FAKE_DEVICES)

        result, error = await _validate_credentials(hass, "user@example.com", "hunter2")

    assert result is client
    assert error is None


async def test_validate_credentials_no_devices(hass: HomeAssistant) -> None:
    """Test that an account without CatLitter devices reports an error."""
    from custom_components.neakasa.config_flow import _validate_credentials

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(return_value=[])

        result, error = await _validate_credentials(hass, "user@example.com", "hunter2")

    assert result is None
    assert error == "no_devices_found"


async def test_validate_credentials_auth_error(hass: HomeAssistant) -> None:
    """Test that auth errors map to the authentication error key."""
    from custom_components.neakasa.config_flow import _validate_credentials
    from custom_components.neakasa.exceptions import (
        NeakasaApiClientAuthenticationError,
    )

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(
            side_effect=NeakasaApiClientAuthenticationError("bad password")
        )

        result, error = await _validate_credentials(hass, "user@example.com", "hunter2")

    assert result is None
    assert error == "authentication"


async def test_validate_credentials_conn_error(hass: HomeAssistant) -> None:
    """Test that connection errors map to the connection error key."""
    from custom_components.neakasa.config_flow import _validate_credentials
    from custom_components.neakasa.exceptions import (
        NeakasaApiClientCommunicationError,
    )

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(
            side_effect=NeakasaApiClientCommunicationError("network down")
        )

        result, error = await _validate_credentials(hass, "user@example.com", "hunter2")

    assert result is None
    assert error == "connection"


def test_async_get_options_flow() -> None:
    """Test that the options flow factory returns a NeakasaOptionsFlow."""
    from custom_components.neakasa.config_flow import NeakasaConfigFlow
    from custom_components.neakasa.options_flow import NeakasaOptionsFlow

    flow = NeakasaConfigFlow()
    assert isinstance(flow.async_get_options_flow(MagicMock()), NeakasaOptionsFlow)


async def test_flow_success_invalid_credentials(
    hass: HomeAssistant,
    mock_get_shared_api: MagicMock,
) -> None:
    """Test that wrong credentials show the auth error on the form."""
    from custom_components.neakasa.exceptions import (
        NeakasaApiClientAuthenticationError,
    )

    with (
        patch(
            "custom_components.neakasa.config_flow.NeakasaAPI",
        ) as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient",
        ) as mock_client_cls,
    ):
        mock_api = mock_api_cls.return_value
        mock_api.connect = AsyncMock()

        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(
            side_effect=NeakasaApiClientAuthenticationError("bad password")
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: FAKE_USERNAME, CONF_PASSWORD: FAKE_PASSWORD},
        )
        assert result2["type"] is FlowResultType.FORM
        assert result2["errors"]["base"] == "authentication"


# ---------------------------------------------------------------------------
# Reconfigure flow
# ---------------------------------------------------------------------------


async def test_reconfigure_flow_show_form(hass: HomeAssistant) -> None:
    """Test that the reconfigure flow renders the credentials form."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:user@example.com",
        data={
            CONF_USERNAME: "user@example.com",
            CONF_PASSWORD: "old-password",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "reconfigure", "entry_id": entry.entry_id},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"


async def test_reconfigure_flow_success(hass: HomeAssistant) -> None:
    """Test that the reconfigure flow updates credentials."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:user@example.com",
        data={
            CONF_USERNAME: "user@example.com",
            CONF_PASSWORD: "old-password",
        },
    )
    entry.add_to_hass(hass)

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(return_value=FAKE_DEVICES)

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "reconfigure", "entry_id": entry.entry_id},
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "new@example.com", CONF_PASSWORD: "new-password"},
        )

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"
    assert entry.data[CONF_USERNAME] == "new@example.com"
    assert entry.data[CONF_PASSWORD] == "new-password"


async def test_reconfigure_flow_invalid_credentials(
    hass: HomeAssistant,
) -> None:
    """Test that reconfigure shows errors for wrong credentials."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.neakasa.exceptions import (
        NeakasaApiClientCommunicationError,
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:user@example.com",
        data={
            CONF_USERNAME: "user@example.com",
            CONF_PASSWORD: "old-password",
        },
    )
    entry.add_to_hass(hass)

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(
            side_effect=NeakasaApiClientCommunicationError("down")
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "reconfigure", "entry_id": entry.entry_id},
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "new@example.com", CONF_PASSWORD: "new-password"},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"]["base"] == "connection"


# ---------------------------------------------------------------------------
# Reauth flow
# ---------------------------------------------------------------------------


async def test_reauth_flow_success(hass: HomeAssistant) -> None:
    """Test that reauthentication updates the entry credentials."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:user@example.com",
        data={
            CONF_USERNAME: "user@example.com",
            CONF_PASSWORD: "old-password",
        },
    )
    entry.add_to_hass(hass)

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(return_value=FAKE_DEVICES)

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "reauth", "entry_id": entry.entry_id},
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "reauth_confirm"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "user@example.com", CONF_PASSWORD: "new-password"},
        )

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "reauth_successful"
    assert entry.data[CONF_PASSWORD] == "new-password"


async def test_reauth_flow_invalid_credentials(hass: HomeAssistant) -> None:
    """Test that reauth shows errors for wrong credentials."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.neakasa.exceptions import (
        NeakasaApiClientAuthenticationError,
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:user@example.com",
        data={
            CONF_USERNAME: "user@example.com",
            CONF_PASSWORD: "old-password",
        },
    )
    entry.add_to_hass(hass)

    with (
        patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls,
        patch(
            "custom_components.neakasa.config_flow.NeakasaApiClient"
        ) as mock_client_cls,
    ):
        mock_api_cls.return_value.connect = AsyncMock()
        client = mock_client_cls.return_value
        client.connect = AsyncMock()
        client.get_devices = AsyncMock(
            side_effect=NeakasaApiClientAuthenticationError("bad")
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "reauth", "entry_id": entry.entry_id},
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "user@example.com", CONF_PASSWORD: "wrong"},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"]["base"] == "authentication"


async def test_validate_credentials_login_rejected(hass: HomeAssistant) -> None:
    """Test that a rejected login maps to the authentication error key."""
    from custom_components.neakasa.api import APIAuthError
    from custom_components.neakasa.config_flow import _validate_credentials

    with patch("custom_components.neakasa.config_flow.NeakasaAPI") as mock_api_cls:
        mock_api_cls.return_value.connect = AsyncMock(
            side_effect=APIAuthError("Invalid username or password.")
        )

        result, error = await _validate_credentials(hass, "user@example.com", "bad")

    assert result is None
    assert error == "authentication"


async def test_reauth_flow_wrong_account(hass: HomeAssistant) -> None:
    """Test that reauth refuses credentials for a different account."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:user@example.com",
        data={CONF_USERNAME: "user@example.com", CONF_PASSWORD: "old-password"},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.neakasa.config_flow._validate_credentials",
        new=AsyncMock(return_value=(MagicMock(), None)),
    ) as validate:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "reauth", "entry_id": entry.entry_id},
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "other@example.com", CONF_PASSWORD: "pw"},
        )

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "wrong_account"
    validate.assert_not_awaited()
    assert entry.data[CONF_USERNAME] == "user@example.com"


async def test_reconfigure_flow_rejects_configured_account(
    hass: HomeAssistant,
) -> None:
    """Test that reconfigure cannot switch to an account another entry uses."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:user@example.com",
        data={CONF_USERNAME: "user@example.com", CONF_PASSWORD: "pw"},
    )
    entry.add_to_hass(hass)
    MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="account:other@example.com",
        data={CONF_USERNAME: "other@example.com", CONF_PASSWORD: "pw"},
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "reconfigure", "entry_id": entry.entry_id},
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: "other@example.com", CONF_PASSWORD: "pw"},
    )

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
