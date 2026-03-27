# src/simulacrum/core/memory.py
from typing import Any, Dict, List, Optional


class Memory:
    """Simple event-based memory store for digital twins."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def add(self, event: Dict[str, Any]) -> None:
        """Append an event to memory."""
        self.events.append(event)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Return events that contain the query string (case-insensitive)."""
        query_lower = query.lower()
        matches = [e for e in self.events if query_lower in str(e).lower()]
        return matches[-limit:]

    def to_dict(self) -> Dict[str, Any]:
        return {"events": self.events}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        m = cls()
        m.events = data.get("events", [])
        return m
