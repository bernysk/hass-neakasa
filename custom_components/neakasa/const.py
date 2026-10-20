from __future__ import annotations

import logging

DOMAIN = "neakasa"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_STATS_LOOKBACK_DAYS = "stats_lookback_days"
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 30
DEFAULT_STATS_LOOKBACK_DAYS = 7
AES_KEY_DEFAULT = b"3J74PRUE5TKPJP32"
AES_IV_DEFAULT = b"QB8GC2X6WK39FF93"

LOGGER = _LOGGER = logging.getLogger(__package__)
