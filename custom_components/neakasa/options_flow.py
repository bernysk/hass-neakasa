"""Options flow for Neakasa."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_STATS_LOOKBACK_DAYS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STATS_LOOKBACK_DAYS,
    MIN_SCAN_INTERVAL,
)


class NeakasaOptionsFlow(OptionsFlow):
    """Handle options for Neakasa integration."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                data={key: int(value) for key, value in user_input.items()}
            )

        options = self.config_entry.options
        current_scan = max(
            MIN_SCAN_INTERVAL, options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        current_lookback = options.get(
            CONF_STATS_LOOKBACK_DAYS, DEFAULT_STATS_LOOKBACK_DAYS
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_scan,
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=300,
                        step=5,
                        unit_of_measurement="seconds",
                        mode=NumberSelectorMode.BOX,
                    ),
                ),
                vol.Required(
                    CONF_STATS_LOOKBACK_DAYS,
                    default=current_lookback,
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=30,
                        step=1,
                        unit_of_measurement="days",
                        mode=NumberSelectorMode.BOX,
                    ),
                ),
            },
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
