"""Flask application entrypoint."""

from __future__ import annotations

import html
import logging

from flask import Flask, Response, jsonify, request

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


def _list_players_payload() -> tuple[dict, int]:
    """Return (body, status) for the players debug list."""
    try:
        player_list = ma_client.list_players()
        simplified = [
            {
                "player_id": player.get("player_id"),
                "name": player.get("display_name") or player.get("name"),
            }
            for player in player_list
        ]
        return {"players": simplified}, 200
    except Exception as exc:
        return {"error": str(exc)}, 500


@app.get("/")
def index() -> Response:
    """Ingress Open Web UI lands on /. Relative links keep HA ingress prefix intact."""
    payload, status = _list_players_payload()
    if "error" in payload:
        err = html.escape(str(payload["error"]))
        body = (
            "<!DOCTYPE html><html><head><meta charset=utf-8>"
            "<title>Music Assistant Alexa Voice</title></head><body>"
            "<h1>Music Assistant Alexa Voice</h1>"
            f"<p>Could not list players: <code>{err}</code></p>"
            "<p>Check <code>ma_url</code> / <code>ma_token</code> in add-on options.</p>"
            '<p><a href="health">health</a> · <a href="players">players (JSON)</a></p>'
            "</body></html>"
        )
        return Response(body, status=status, mimetype="text/html")

    rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(p.get('name') or ''))}</td>"
        f"<td><code>{html.escape(str(p.get('player_id') or ''))}</code></td>"
        "</tr>"
        for p in payload.get("players", [])
    )
    body = (
        "<!DOCTYPE html><html><head><meta charset=utf-8>"
        "<title>Music Assistant Alexa Voice</title>"
        "<style>"
        "body{font-family:system-ui,sans-serif;margin:2rem;line-height:1.4}"
        "table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:.4rem .75rem;text-align:left}"
        "code{font-size:.95em}"
        "</style></head><body>"
        "<h1>Music Assistant Alexa Voice</h1>"
        "<p>MA connectivity OK. Copy a <code>player_id</code> into "
        "<code>default_player_id</code> or <code>player_aliases</code>.</p>"
        f"<table><thead><tr><th>Name</th><th>player_id</th></tr></thead>"
        f"<tbody>{rows or '<tr><td colspan=2>No players found</td></tr>'}</tbody></table>"
        '<p><a href="health">health</a> · <a href="players">players (JSON)</a></p>'
        "</body></html>"
    )
    return Response(body, status=200, mimetype="text/html")


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
    payload, status = _list_players_payload()
    return jsonify(payload), status
