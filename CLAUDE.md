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
`…CommunicationError`). The coordinator retries communication errors a few
times with backoff, re-logs in once on an expired session, and raises
`ConfigEntryAuthFailed` (which starts reauth) when the credentials are
rejected. User-triggered commands raise translated `HomeAssistantError`s.

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