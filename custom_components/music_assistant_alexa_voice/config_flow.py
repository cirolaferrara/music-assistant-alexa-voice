"""Config flow for Music Assistant Alexa Voice."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_ADDON_URL, DOMAIN


async def _validate_addon_url(hass: HomeAssistant, addon_url: str) -> None:
    session = async_get_clientsession(hass)
    health_url = f"{addon_url.rstrip('/')}/health"
    async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
        if response.status != 200:
            raise ValueError(f"Add-on health check failed with status {response.status}")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            addon_url = user_input["addon_url"].strip()
            access_token = user_input["access_token"].strip()
            if not access_token:
                errors["base"] = "missing_token"
            else:
                try:
                    await _validate_addon_url(self.hass, addon_url)
                except (aiohttp.ClientError, TimeoutError, ValueError):
                    errors["base"] = "cannot_connect"

                if not errors:
                    await self.async_set_unique_id(access_token)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="Music Assistant Alexa Voice",
                        data={
                            "addon_url": addon_url,
                            "access_token": access_token,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("addon_url", default=DEFAULT_ADDON_URL): str,
                    vol.Required("access_token"): str,
                }
            ),
            errors=errors,
        )
