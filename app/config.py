"""Application configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


def _load_player_aliases(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("PLAYER_ALIASES must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("PLAYER_ALIASES must be a JSON object")
    return {str(k).lower(): str(v) for k, v in parsed.items()}


@dataclass(frozen=True)
class Settings:
    ma_url: str
    ma_token: str
    default_player_id: str
    player_aliases: dict[str, str] = field(default_factory=dict)
    skill_verify_requests: bool = True
    port: int = 5000

    @classmethod
    def from_env(cls) -> "Settings":
        ma_url = os.environ.get("MA_URL", "http://host.docker.internal:8095").rstrip("/")
        ma_token = os.environ.get("MA_TOKEN", "")
        default_player_id = os.environ.get("DEFAULT_PLAYER_ID", "")
        if not ma_token:
            raise ValueError("MA_TOKEN is required")
        if not default_player_id:
            raise ValueError("DEFAULT_PLAYER_ID is required")
        return cls(
            ma_url=ma_url,
            ma_token=ma_token,
            default_player_id=default_player_id,
            player_aliases=_load_player_aliases(os.environ.get("PLAYER_ALIASES")),
            skill_verify_requests=os.environ.get("SKILL_VERIFY_REQUESTS", "true").lower()
            in {"1", "true", "yes", "on"},
            port=int(os.environ.get("PORT", "5000")),
        )
