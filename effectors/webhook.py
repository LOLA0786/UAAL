import requests
from typing import Dict, Any
from .base import Effector


class WebhookEffector(Effector):
    """Generic webhook effector for arbitrary services."""

    def deliver(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = payload["url"]
        data = payload.get("data", {})

        r = requests.post(url, json=data, timeout=5)
        return {"status": r.status_code, "url": url}
