"""Application configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_ha_options() -> dict[str, object]:
    options_path = Path("/data/options.json")
    if not options_path.exists():
        return {}
    try:
        with options_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _option(options: dict[str, object], *keys: str, default: str = "") -> str:
    for key in keys:
        if key in options and options[key] is not None:
            value = options[key]
            return str(value).strip()
    return default


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
        options = _load_ha_options()

        ma_url = _option(options, "ma_url") or os.environ.get(
            "MA_URL", "http://08524bff_music_assistant:8095"
        )
        ma_url = ma_url.rstrip("/")

        ma_token = _option(options, "ma_token") or os.environ.get("MA_TOKEN", "")
        default_player_id = _option(options, "default_player_id") or os.environ.get(
            "DEFAULT_PLAYER_ID", ""
        )
        aliases_raw = _option(options, "player_aliases") or os.environ.get("PLAYER_ALIASES")
        port_raw = _option(options, "port") or os.environ.get("PORT", "5000")
        verify_raw = _option(options, "skill_verify_requests") or os.environ.get(
            "SKILL_VERIFY_REQUESTS", "true"
        )

        if not ma_token:
            raise ValueError("MA_TOKEN is required")
        if not default_player_id:
            raise ValueError("DEFAULT_PLAYER_ID is required")

        return cls(
            ma_url=ma_url,
            ma_token=ma_token,
            default_player_id=default_player_id,
            player_aliases=_load_player_aliases(aliases_raw),
            skill_verify_requests=verify_raw.lower() in {"1", "true", "yes", "on"},
            port=int(port_raw),
        )
