"""Flask application entrypoint."""

from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from app.config import Settings
from app.ma_client import MusicAssistantClient
from app.skill.router import AlexaSkillRouter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

settings = Settings.from_env()
ma_client = MusicAssistantClient(settings.ma_url, settings.ma_token)
router = AlexaSkillRouter(settings, ma_client)

app = Flask(__name__)


@app.post("/alexa")
def alexa() -> tuple[dict, int]:
    body = request.get_json(silent=True) or {}
    response = router.handle(body)
    return jsonify(response), 200


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return jsonify({"status": "ok"}), 200


@app.get("/players")
def players() -> tuple[dict, int]:
    """Debug endpoint to list MA players and verify connectivity."""
    try:
        player_list = ma_client.list_players()
        simplified = [
            {
                "player_id": player.get("player_id"),
                "name": player.get("display_name") or player.get("name"),
            }
            for player in player_list
        ]
        return jsonify({"players": simplified}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
