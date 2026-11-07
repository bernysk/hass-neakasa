# Known bugs

Review of v1.6.1 (`21a6d5b`), 2026-11-07. B1–B6, B10 and B11 are fixed in
1.7.0, ported from upstream; see the **Status** line of each entry. Codex (GPT-5) produced the findings and
Claude checked each one against the code. **Verdict:** Confirmed (read in the code),
Plausible (the code allows it, but it has not been seen happening), or Edge (real
but unlikely for a single-account, single-box install). "Upstream" means
[tabascoz/hass-neakasa](https://github.com/tabascoz/hass-neakasa), which has
already fixed several of these.

## High

### B1. Web-API token expiry is classified as a network error
- **Where:** `custom_components/neakasa/api_client.py:44`
- **Verdict:** Confirmed. Upstream fix: `9db5675`.
- **Status:** Fixed in 1.7.0: `TokenInvalid` / `token is abnormal` now count as session expiry and trigger a full login.
- `/catbox/record` answers `TokenInvalid: token is abnormal` when the login token
  ages out. The message contains neither `auth` nor `session`, so it becomes a
  `CommunicationError`. The value cacher then serves the old records for up to 4 h.
  After that the device drops out of the update and its entities go unavailable.
  No re-login is ever attempted. Cat weights and last usage go silently stale.

### B2. Per-device failures never reach the recovery paths
- **Where:** `custom_components/neakasa/coordinator.py:497-505`
- **Verdict:** Confirmed. Upstream fix: `9db5675`.
- **Status:** Fixed in 1.7.0: device-level session, auth and identityId errors are raised to the recovery path.
- `asyncio.gather(return_exceptions=True)` logs and drops every device-level
  exception, including session-expired, auth and `identityId is blank`. A dead
  session therefore produces a "successful" update with no devices, so all entities
  go unavailable. No retry or re-login runs.

### B3. Every session failure does a full login, with no cooldown
- **Where:** `coordinator.py:530-556`, `coordinator.py:335-348`, `api_manager.py:66-71`
- **Verdict:** Confirmed. Upstream fix: `e552ab2`, plus later work in `docs/cloud-session-churn.md`.
- **Status:** Fixed in 1.7.0: the IoT token is renewed first, full logins are limited to one per 10 min (`FULL_LOGIN_COOLDOWN_SECONDS`), and `force_reconnect_api(stale=)` reuses a client that another caller already replaced.
- Each full login mints a new account session, which logs the official Neakasa app
  out. The coordinator and `_run_command` call `force_reconnect_api` on every
  expiry. They never try the one-call `sid -> iotToken` renewal first, and nothing
  limits how often they re-login. Upstream measured five logins in eight minutes
  and the app being kicked out about once a minute. `force_reconnect_api` also
  drops the cached client before it takes the account lock. Two commands that fail
  at the same time therefore log in twice (Codex finding 7).

## Medium

### B4. The value cacher hides auth and session errors
- **Where:** `custom_components/neakasa/value_cacher.py:92`
- **Verdict:** Confirmed.
- **Status:** Fixed in 1.7.0: `ValueCacher(reraise=...)` lets session and auth errors through.
- Any exception falls back to the cached value: properties for up to 30 min,
  records for up to 4 h. This hides the errors that should trigger recovery. Only
  communication errors should fall back to the cache. Session and auth errors
  should be re-raised.

### B5. `identityId is blank` on a button or switch is not recovered
- **Where:** `coordinator.py:335-348`, `api.py:369-372`
- **Verdict:** Confirmed. Codex missed this one. Upstream fix: `abddd6f`.
- **Status:** Fixed in 1.7.0: `_iot_request` renews the IoT token once and retries.
- `_run_command` retries only on `SessionExpiredError`. An aged IoT token gives
  `identityId is blank`, which is a `CommunicationError`, so the press fails with
  an error. Upstream refreshes the IoT token once inside `_iot_request` and retries.
  That covers both polling and commands.

### B6. `clear_shared_api` removes the account lock
- **Where:** `custom_components/neakasa/api_manager.py:62`
- **Verdict:** Confirmed. Upstream fix: `e552ab2` (registry lock; never drop the lock).
- **Status:** Fixed in 1.7.0: the account lock is created under a registry lock and kept when the client is cleared.
- If the client is cleared while a login holds the lock, the next caller creates a
  new lock and logs in at the same time. The result is two sessions, and the older
  client can overwrite the newer one in the cache. Lock creation is also not
  atomic (`api_manager.py:31-33`).

### B7. A changed last-use time is recorded before the new record arrives
- **Where:** `coordinator.py:428-433`
- **Verdict:** Plausible.
- If the IoT side reports a visit before the web API has published its record,
  the records refetch returns the old list. The staleness flag is cleared anyway.
  The new cat weight then shows up only after the 30-minute refresh. Fix: keep the
  records stale until the newest record matches `last_use`.

## Low

### B8. Missing properties are reported as valid values
- **Where:** `coordinator.py:194-210`
- **Verdict:** Plausible.
- An empty or partial properties response becomes `bin_full=False`,
  `sand_level=0` and so on, and the entities stay available. Only a missing
  snapshot marks them unavailable.

### B9. The auto-clean switch stays available without `cleanCfg`
- **Where:** `switch/auto_clean.py`, `coordinator.py:178-185`
- **Verdict:** Confirmed.
- The warning says the switch "will be unavailable", but no `available`
  override exists. Toggling it then sends `{"active": x}` alone. Whether the cloud
  then wipes the schedule is unverified. An M1 normally reports `cleanCfg`.

### B10. Release metadata disagrees
- **Where:** `manifest.json:10` (`1.4.1`), `pyproject.toml:16` (`1.3.1`), `CHANGELOG.md` (`1.6.1`)
- **Verdict:** Confirmed.
- **Status:** Fixed in 1.7.0: all three files now say 1.7.0.
- Home Assistant shows 1.4.1 for the 1.6.1 code.

### B11. Logs and diagnostics leak identifiers
- **Where:** `api_manager.py:39-52` (logs the username/email), `diagnostics.py:39` (raw `device_ids`)
- **Verdict:** Confirmed. Upstream fix: `dd3193b` (diagnostics), `log_redact.py` (logs).
- **Status:** Fixed in 1.7.0: logs no longer name the account, and diagnostics redact device IDs.

### B12. Config-flow validation is an extra full login
- **Where:** `config_flow.py:23-43`
- **Verdict:** Confirmed, low impact.
- Setup, reauth and reconfigure each log in once to validate, then log in again
  on reload. It happens once per flow and does not repeat.

### B13. Only the first 20 bound devices are discovered
- **Where:** `coordinator.py:366`, `config_flow.py:35`, `api.py:393`
- **Verdict:** Edge.
- There is no pagination over `/uc/listBindingByAccount`.

### B14. Migration can keep a disabled entry as the owner
- **Where:** `migration.py:18-28`
- **Verdict:** Edge.
- Applies only to V1 per-device entries, where one is disabled and listed first.
  Installs that have already migrated are not affected.

### B15. A device claim outlives losing access to the device
- **Where:** `device_claims.py:51-55`
- **Verdict:** Edge.
- If a box moves from account A to account B, B keeps skipping it while A's entry
  is still enabled. A's registry link reserves the box.
