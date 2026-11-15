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
from app.skill.query_parse import split_query_and_room

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
                    f"Music Assistant è pronto. Dimmi cosa vuoi ascoltare su {player_name}."
                ),
                session_attributes,
            )

        if request_type == "SessionEndedRequest":
            return empty_response()

        intent_name = get_intent_name(body)
        if not intent_name:
            return speech_response("Scusa, non ho capito.")

        active_player_id = session_attributes.get("active_player_id") or self._settings.default_player_id

        try:
            if intent_name == "PlayMusicIntent":
                return self._play_music(body, session_attributes, active_player_id)
            if intent_name == "PlayInRoomIntent":
                return self._play_in_room(body, session_attributes, active_player_id)
            if intent_name == "AMAZON.PauseIntent":
                self._ma.pause(active_player_id)
                return with_session_attributes(speech_response("In pausa."), session_attributes)
            if intent_name == "AMAZON.ResumeIntent":
                self._ma.play(active_player_id)
                return with_session_attributes(
                    speech_response("Riprendo la riproduzione."),
                    session_attributes,
                )
            if intent_name in {"AMAZON.StopIntent", "AMAZON.CancelIntent"}:
                self._ma.stop(active_player_id)
                return with_session_attributes(speech_response("Fermato."), session_attributes)
            if intent_name == "NextTrackIntent":
                self._ma.next_track(active_player_id)
                return with_session_attributes(
                    speech_response("Passo al brano successivo."),
                    session_attributes,
                )
            if intent_name == "PreviousTrackIntent":
                self._ma.previous_track(active_player_id)
                return with_session_attributes(
                    speech_response("Torno al brano precedente."),
                    session_attributes,
                )
            if intent_name == "AMAZON.HelpIntent":
                return speech_response(
                    "Puoi dire: riproduci Fleetwood Mac, riproduci jazz in cucina, "
                    "riproduci in cucina, pausa, riprendi, stop, avanti o indietro."
                )
            if intent_name == "AMAZON.FallbackIntent":
                return speech_response("Scusa, non ho capito. Prova a chiedermi di riprodurre qualcosa.")
        except MusicAssistantError as exc:
            logger.warning("Intent %s failed: %s", intent_name, exc)
            return with_session_attributes(
                speech_response(f"Scusa, non sono riuscito a farlo. {exc}"),
                session_attributes,
            )
        except Exception:
            logger.exception("Unexpected Alexa intent failure: %s", intent_name)
            return with_session_attributes(
                speech_response("Scusa, qualcosa è andato storto nella comunicazione con Music Assistant."),
                session_attributes,
            )

        return speech_response("Scusa, non ho capito.")

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
                speech_response("Cosa vuoi che riproduca?"),
                session_attributes,
            )

        if not room:
            query, room = split_query_and_room(query)

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
            text = f"Riproduco {label} su {player_name}."
        else:
            text = f"Riproduco {label}."
        return with_session_attributes(speech_response(text), session_attributes)

    def _play_in_room(
        self,
        body: dict[str, Any],
        session_attributes: dict[str, Any],
        active_player_id: str,
    ) -> dict[str, Any]:
        room = get_slot_value(body, "Room")
        if not room:
            return with_session_attributes(
                speech_response("In quale stanza devo riprodurre?"),
                session_attributes,
            )

        player_id, player_name = self._ma.resolve_player(
            room,
            default_player_id=active_player_id,
            aliases=self._settings.player_aliases,
        )
        self._ma.play(player_id)
        session_attributes["active_player_id"] = player_id
        return with_session_attributes(
            speech_response(f"Riproduco su {player_name}."),
            session_attributes,
        )

