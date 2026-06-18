"""Music Assistant Alexa Voice integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .http import AlexaSkillView

type MusicAssistantAlexaVoiceConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: MusicAssistantAlexaVoiceConfigEntry) -> bool:
    """Set up the cloud proxy for the add-on."""
    addon_url = entry.data["addon_url"]
    access_token = entry.data["access_token"]
    view = AlexaSkillView(addon_url, access_token)
    hass.http.register_view(view)
    entry.runtime_data = view
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MusicAssistantAlexaVoiceConfigEntry) -> bool:
    """Unload the integration."""
    view = entry.runtime_data
    if view is not None:
        hass.http.views.pop(view.name, None)
    return True
