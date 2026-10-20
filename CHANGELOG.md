# Changelog

All notable changes to this fork are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.6.0] - 2026-10-20

### Fixed

- A Neakasa cloud outage no longer stalls updates for about an hour: failed polls are retried three times (2/4/8 s) and the entities are then marked unavailable.
- After a session expires, the integration logs in again once instead of looping.
- A wrong password during setup shows "Invalid username or password" instead of "Unknown error", and rejected credentials now start the re-authentication flow.
- Diagnostics downloads no longer contain the account email address.
- Cat weight sensors no longer record 0 kg when there is no recent visit, and always use the newest visit.
- Entities of a device that is missing from the latest update are shown as unavailable instead of "off".
- The "Statistics lookback" option is now applied (it was always 7 days).
- Re-authenticating or reconfiguring reloads the integration once instead of twice; re-authentication refuses a different account and reconfiguring refuses an account that is already set up.
- Every request has a 30 s timeout, and network errors or unexpected responses no longer log a traceback on every poll.

### Changed

- The minimum polling interval is 30 s (previously 10 s); lower saved values are raised to 30 s.
- Entries created by old versions (one per litter box) are merged into one entry per account, keeping their devices and entities.

### Added

- Readable error messages when a switch or button command fails; an expired session is renewed once before giving up.
- Weight sensors for cats added after setup appear without restarting Home Assistant.
- Device data is refreshed right after pressing Clean or Level.
- Devices show their model in the device registry.
- Labels and descriptions for the integration options in English, German, French and Polish.

## [1.5.0]

### Changed

- Repository metadata (code owner, documentation and issue tracker links, README) now points to this fork.
