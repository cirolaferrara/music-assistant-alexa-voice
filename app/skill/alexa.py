"""Alexa request/response helpers."""

from __future__ import annotations

from typing import Any


def speech_response(text: str, *, end_session: bool = True) -> dict[str, Any]:
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session,
        },
    }


def empty_response(*, end_session: bool = True) -> dict[str, Any]:
    return {
        "version": "1.0",
        "response": {
            "shouldEndSession": end_session,
        },
    }


def get_intent_name(body: dict[str, Any]) -> str | None:
    request = body.get("request") or {}
    if request.get("type") != "IntentRequest":
        return None
    intent = request.get("intent") or {}
    return intent.get("name")


def get_slot_value(body: dict[str, Any], slot_name: str) -> str | None:
    request = body.get("request") or {}
    intent = request.get("intent") or {}
    slots = intent.get("slots") or {}
    slot = slots.get(slot_name) or {}
    value = slot.get("value")
    return value.strip() if isinstance(value, str) and value.strip() else None


def get_session_attributes(body: dict[str, Any]) -> dict[str, Any]:
    session = body.get("session") or {}
    attributes = session.get("attributes") or {}
    return dict(attributes)


def with_session_attributes(response: dict[str, Any], attributes: dict[str, Any]) -> dict[str, Any]:
    if attributes:
        response["sessionAttributes"] = attributes
    return response
