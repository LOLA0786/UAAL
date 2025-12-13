from typing import Dict, Any
from .base import Effector


class GoogleCalendarEffector(Effector):
    """Mock Google Calendar effector (real API can be added easily)."""

    def deliver(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = payload["title"]
        start = payload.get("start")

        print(f"[GCAL] Creating: {title} at {start}")
        return {"status": "created", "event_title": title}
