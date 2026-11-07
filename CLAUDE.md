# CLAUDE.md

Guidance for Claude Code agents working in this repository.

## Always read `CODE_STYLE.md` first

Before creating, renaming or restructuring any file/class/function, **read
[`CODE_STYLE.md`](./CODE_STYLE.md)**. It is the single source of truth for
conventions: language, file organisation, naming, typing, docstrings,
comments, translations, lint workflow.

For user-facing topics (what's included, how to install, supported devices),
see [`README.md`](./README.md).

## Verification workflow

**After every code change, always run lint then tests, in that order, before
declaring the task done:**

```bash
uv run ruff format . && uv run ruff check . --fix && uv run mypy custom_components/neakasa && uv run pytest
```

- The lint commands run `ruff format`, `ruff check --fix` and `mypy` (config
  in `pyproject.toml`). Fix any failure and re-run before moving on.
- Both gates mirror CI.

## Architecture

The integration follows the HA `DataUpdateCoordinator` pattern, with one
config entry per Neakasa account covering all of its litter boxes:

```
__init__.py         → async_setup_entry / async_unload_entry; forwards to platforms
migration.py        → config entry migrations (V1 per-device → V2.2 per-account)
config_flow.py      → user / reauth / reconfigure flows (credentials only)
options_flow.py     → scan_interval (≥30s) and stats_lookback_days
coordinator.py      → polls all CatLitter devices; data is dict[iot_id, NeakasaDeviceSnapshot]
api_manager.py      → caches one authenticated NeakasaApiClient per account
api_client.py       → NeakasaApiClient: wraps NeakasaAPI and translates its errors
api.py              → NeakasaAPI: login, Aliyun IoT gateway calls, Neakasa web API
iot_gateway.py      → AliyunIoTClient: Aliyun API Gateway HMAC request signing (aiohttp)
api_encryption.py   → AES-CBC helpers for the web API login token
value_cacher.py     → time-based cache with refresh/discard windows
entity.py           → NeakasaEntity base class and neakasa_device_info()
sensor/ switch/ binary_sensor/ button/
                    → one entity class per file, all subclassing NeakasaEntity
diagnostics.py      → redacted diagnostics download
```

There is no Aliyun SDK dependency; requests are signed by hand in
`iot_gateway.py`.

### Errors and recovery

`NeakasaAPI` raises `APIAuthError` / `APIConnectionError`; `NeakasaApiClient`
translates them into the `exceptions/` hierarchy
(`NeakasaApiClientAuthenticationError`, `…SessionExpiredError`,
`…CommunicationError`). The web API's `TokenInvalid: token is abnormal`
counts as session expiry. The coordinator retries communication errors a few
times with backoff. On an expired session it first renews the IoT token
(`refresh_session`, one call), and logs in again only when that fails or
the login token itself was rejected. Every full login creates a new account
session, which signs the official app out, so full logins are limited to one
per `FULL_LOGIN_COOLDOWN_SECONDS` (600 s), including the implicit one in
`_get_client` when the cached client lost its session. `_iot_request`
renews the token itself on `identityId is blank`. The caches re-raise
session and auth errors instead of serving stale values, and device-level
session errors are not swallowed by `asyncio.gather`. Rejected credentials
raise `ConfigEntryAuthFailed`, which starts reauth. User-triggered commands
use the same recovery and raise translated `HomeAssistantError`s.

### Coordinator data

`NeakasaCoordinator.data` maps each device's `iotId` to a
`NeakasaDeviceSnapshot`. Device properties are fetched on every poll (with a
30 min fallback on errors via `ValueCacher`); usage records are cached for
30 min and invalidated when `catLeft.time` changes.

### Tests

Home Assistant's test plugin does not run on Windows (it needs `fcntl` and
`resource`); run the suite on Linux, macOS, WSL or in CI.

## Wave migration plan

This integration is being incrementally modernised against the reference
implementation at `ha-neakasa-litterbox`. See the Wave plan in the PR
description for the ordered migration steps.