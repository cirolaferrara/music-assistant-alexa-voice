#!/usr/bin/env python3
"""List Music Assistant players using MA_URL and MA_TOKEN from the environment."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from app.ma_client import MusicAssistantClient


def main() -> int:
    url = os.environ.get("MA_URL")
    token = os.environ.get("MA_TOKEN")
    if not url or not token:
        print("Set MA_URL and MA_TOKEN in .env first.", file=sys.stderr)
        return 1

    client = MusicAssistantClient(url, token)
    players = client.list_players()
    print(json.dumps(players, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
