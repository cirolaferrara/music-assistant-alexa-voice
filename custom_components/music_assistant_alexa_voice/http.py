"""HTTP proxy view for Alexa -> add-on."""

from __future__ import annotations

import logging

import aiohttp
from aiohttp import web
from homeassistant.components.http import HomeAssistantView

_LOGGER = logging.getLogger(__name__)


class AlexaSkillView(HomeAssistantView):
    """Expose the add-on Alexa endpoint through Home Assistant HTTP."""

    requires_auth = False
    url = "/api/music_assistant_alexa_voice/alexa"
    name = "api:music_assistant_alexa_voice:alexa"

    def __init__(self, addon_url: str, access_token: str) -> None:
        self._addon_url = f"{addon_url.rstrip('/')}/alexa"
        self._access_token = access_token

    def _authorized(self, request: web.Request) -> bool:
        if not self._access_token:
            return True
        query_token = request.query.get("token")
        header = request.headers.get("Authorization", "")
        bearer = header[7:] if header.startswith("Bearer ") else header
        return query_token == self._access_token or bearer == self._access_token

    async def post(self, request: web.Request) -> web.Response:
        if not self._authorized(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        body = await request.read()
        headers = {"Content-Type": request.headers.get("Content-Type", "application/json")}

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session, session.post(
                self._addon_url,
                data=body,
                headers=headers,
            ) as response:
                response_body = await response.read()
                content_type = response.headers.get("Content-Type", "application/json")
                return web.Response(
                    body=response_body,
                    status=response.status,
                    content_type=content_type,
                )
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to reach Music Assistant Alexa Voice add-on: %s", err)
            return web.json_response(
                {
                    "version": "1.0",
                    "response": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": "Sorry, the Music Assistant Alexa Voice service is unavailable.",
                        },
                        "shouldEndSession": True,
                    },
                },
                status=503,
            )
