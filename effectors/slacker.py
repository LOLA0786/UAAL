from typing import Dict, Any
from .base import Effector


class SlackEffector(Effector):
    """Mock Slack effector — replace with Slack Web API later."""

    def deliver(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        channel = payload["channel"]
        text = payload["text"]

        print(f"[SLACK] #{channel}: {text}")
        return {"status": "posted", "channel": channel}
