"""Music Assistant HTTP JSON-RPC client."""

from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MusicAssistantError(Exception):
    """Raised when Music Assistant returns an error response."""


class MusicAssistantClient:
    def __init__(self, base_url: str, token: str, timeout: float = 20.0) -> None:
        self._api_url = f"{base_url.rstrip('/')}/api"
        self._token = token
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def command(self, name: str, args: dict[str, Any] | None = None) -> Any:
        payload = {
            "message_id": str(uuid.uuid4()),
            "command": name,
            "args": args or {},
        }
        response = self._client.post(
            self._api_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        body = response.json()
        # MA 2.x HTTP may return a bare result (list/dict) or a wrapped
        # {"message_id", "result"} / error payload.
        if isinstance(body, list):
            return body
        if not isinstance(body, dict):
            return body
        if "error" in body:
            raise MusicAssistantError(body["error"])
        if "error_code" in body:
            raise MusicAssistantError(body.get("details") or body["error_code"])
        if "result" in body:
            return body.get("result")
        return body

    def list_players(self) -> list[dict[str, Any]]:
        result = self.command("players/all")
        return result or []

    def search(self, query: str, limit: int = 5) -> dict[str, Any]:
        return self.command(
            "music/search",
            {
                "search_query": query,
                "media_types": ["track", "album", "artist", "playlist"],
                "limit": limit,
            },
        ) or {}

    def play_media(
        self,
        queue_id: str,
        media: str,
        *,
        radio_mode: bool = False,
    ) -> None:
        self.command(
            "player_queues/play_media",
            {
                "queue_id": queue_id,
                "media": media,
                "radio_mode": radio_mode,
            },
        )

    def pause(self, queue_id: str) -> None:
        self.command("player_queues/pause", {"queue_id": queue_id})

    def play(self, queue_id: str) -> None:
        self.command("player_queues/play", {"queue_id": queue_id})

    def stop(self, queue_id: str) -> None:
        self.command("player_queues/stop", {"queue_id": queue_id})

    def next_track(self, queue_id: str) -> None:
        self.command("player_queues/next", {"queue_id": queue_id})

    def previous_track(self, queue_id: str) -> None:
        self.command("player_queues/previous", {"queue_id": queue_id})

    def resolve_player(
        self,
        room: str | None,
        *,
        default_player_id: str,
        aliases: dict[str, str],
    ) -> tuple[str, str]:
        """Return (player_id, display_name)."""
        if not room:
            players = self.list_players()
            for player in players:
                if player.get("player_id") == default_player_id:
                    return (
                        default_player_id,
                        player.get("display_name") or player.get("name") or default_player_id,
                    )
            return default_player_id, default_player_id

        key = room.strip().lower()
        if key in aliases:
            player_id = aliases[key]
            players = self.list_players()
            for player in players:
                if player.get("player_id") == player_id:
                    return player_id, player.get("display_name") or player.get("name") or player_id
            return player_id, player_id

        players = self.list_players()
        for player in players:
            display = (player.get("display_name") or player.get("name") or "").lower()
            player_id = player.get("player_id", "")
            if key in display or key in player_id.lower():
                return player_id, player.get("display_name") or player.get("name") or player_id

        raise MusicAssistantError(f"No Music Assistant player matched '{room}'")

    def pick_media(self, search_result: dict[str, Any]) -> tuple[str, str, bool]:
        """Return (uri, label, radio_mode)."""
        for media_type, radio_mode in (
            ("tracks", False),
            ("albums", False),
            ("playlists", False),
            ("artists", True),
        ):
            items = search_result.get(media_type) or []
            if not items:
                continue
            item = items[0]
            uri = item.get("uri")
            if not uri:
                continue
            label = item.get("name") or uri
            return uri, label, radio_mode
        raise MusicAssistantError("No playable results found for that request")
