"""Alexa intent routing."""

from __future__ import annotations

import logging
from typing import Any

from app.config import Settings
from app.ma_client import MusicAssistantClient, MusicAssistantError
from app.skill.alexa import (
    empty_response,
    get_intent_name,
    get_session_attributes,
    get_slot_value,
    speech_response,
    with_session_attributes,
)

logger = logging.getLogger(__name__)


class AlexaSkillRouter:
    def __init__(self, settings: Settings, ma: MusicAssistantClient) -> None:
        self._settings = settings
        self._ma = ma

    def handle(self, body: dict[str, Any]) -> dict[str, Any]:
        request = body.get("request") or {}
        request_type = request.get("type")
        session_attributes = get_session_attributes(body)

        if request_type == "LaunchRequest":
            player_id, player_name = self._ma.resolve_player(
                None,
                default_player_id=self._settings.default_player_id,
                aliases=self._settings.player_aliases,
            )
            session_attributes["active_player_id"] = player_id
            return with_session_attributes(
                speech_response(
                    f"Music Assistant is ready. Ask me to play something on {player_name}."
                ),
                session_attributes,
            )

        if request_type == "SessionEndedRequest":
            return empty_response()

        intent_name = get_intent_name(body)
        if not intent_name:
            return speech_response("Sorry, I didn't understand that.")

        active_player_id = session_attributes.get("active_player_id") or self._settings.default_player_id

        try:
            if intent_name == "PlayMusicIntent":
                return self._play_music(body, session_attributes, active_player_id)
            if intent_name == "AMAZON.PauseIntent":
                self._ma.pause(active_player_id)
                return with_session_attributes(speech_response("Paused."), session_attributes)
            if intent_name == "AMAZON.ResumeIntent":
                self._ma.play(active_player_id)
                return with_session_attributes(
                    speech_response("Resuming playback."),
                    session_attributes,
                )
            if intent_name in {"AMAZON.StopIntent", "AMAZON.CancelIntent"}:
                self._ma.stop(active_player_id)
                return with_session_attributes(speech_response("Stopped."), session_attributes)
            if intent_name == "NextTrackIntent":
                self._ma.next_track(active_player_id)
                return with_session_attributes(
                    speech_response("Skipping to the next track."),
                    session_attributes,
                )
            if intent_name == "PreviousTrackIntent":
                self._ma.previous_track(active_player_id)
                return with_session_attributes(
                    speech_response("Going back to the previous track."),
                    session_attributes,
                )
            if intent_name == "AMAZON.HelpIntent":
                return speech_response(
                    "You can say play Fleetwood Mac, play jazz in the kitchen, pause, resume, stop, next, or previous."
                )
            if intent_name == "AMAZON.FallbackIntent":
                return speech_response("Sorry, I didn't catch that. Try asking me to play something.")
        except MusicAssistantError as exc:
            logger.warning("Intent %s failed: %s", intent_name, exc)
            return with_session_attributes(
                speech_response(f"Sorry, I couldn't do that. {exc}"),
                session_attributes,
            )
        except Exception:
            logger.exception("Unexpected Alexa intent failure: %s", intent_name)
            return with_session_attributes(
                speech_response("Sorry, something went wrong talking to Music Assistant."),
                session_attributes,
            )

        return speech_response("Sorry, I didn't understand that.")

    def _play_music(
        self,
        body: dict[str, Any],
        session_attributes: dict[str, Any],
        active_player_id: str,
    ) -> dict[str, Any]:
        query = get_slot_value(body, "Query")
        room = get_slot_value(body, "Room")
        if not query:
            return with_session_attributes(
                speech_response("What would you like me to play?"),
                session_attributes,
            )

        player_id, player_name = self._ma.resolve_player(
            room,
            default_player_id=active_player_id,
            aliases=self._settings.player_aliases,
        )
        search_result = self._ma.search(query)
        uri, label, radio_mode = self._ma.pick_media(search_result)
        self._ma.play_media(player_id, uri, radio_mode=radio_mode)
        session_attributes["active_player_id"] = player_id

        if room:
            text = f"Playing {label} on {player_name}."
        else:
            text = f"Playing {label}."
        return with_session_attributes(speech_response(text), session_attributes)
