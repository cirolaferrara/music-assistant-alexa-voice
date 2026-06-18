"""Parse room names from free-text Alexa queries."""

from __future__ import annotations

import re

# AMAZON.SearchQuery cannot share an utterance with other slots, so room names
# may appear inside the query text, e.g. "jazz in the kitchen".
_ROOM_SUFFIX_PATTERNS = (
    re.compile(r"^(.+?)\s+in\s+the\s+(.+)$", re.IGNORECASE),
    re.compile(r"^(.+?)\s+in\s+(.+)$", re.IGNORECASE),
    re.compile(r"^(.+?)\s+on\s+(.+)$", re.IGNORECASE),
)


def split_query_and_room(query: str) -> tuple[str, str | None]:
    """Return (search_query, room) when the query ends with a room phrase."""
    text = query.strip()
    if not text:
        return "", None

    for pattern in _ROOM_SUFFIX_PATTERNS:
        match = pattern.match(text)
        if not match:
            continue
        search_query = match.group(1).strip()
        room = match.group(2).strip()
        if search_query and room:
            return search_query, room

    return text, None
