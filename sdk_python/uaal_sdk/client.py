import requests
from typing import Optional, Dict, Any


class UAALClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["x-api-key"] = self.api_key
        return h

    def send_action(
        self,
        adapter: str,
        agent_output: Dict[str, Any],
        require_approval: bool = False,
        user_id: Optional[str] = None,
    ):
        payload = {
            "adapter": adapter,
            "agent_output": agent_output,
            "require_approval": require_approval,
            "user_id": user_id,
        }
        r = requests.post(
            f"{self.base_url}/api/v1/actions",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_actions(self, limit: int = 100):
        r = requests.get(
            f"{self.base_url}/api/v1/actions?limit={limit}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()
