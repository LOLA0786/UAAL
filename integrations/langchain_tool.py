import requests
import uuid
from datetime import datetime

class UAALTool:
    def __init__(self, api_key: str, endpoint="http://127.0.0.1:8000/api/v1/actions"):
        self.api_key = api_key
        self.endpoint = endpoint

    def send_action(self, name: str, params: dict, agent="langchain-agent", reasoning=""):
        payload = {
            "adapter": "langchain",
            "agent_output": {
                "assistant_id": agent,
                "intent": name,
                "target": {"type": "generic", "attributes": params},
                "explanation": reasoning,
                "confidence": 0.9,
            },
        }

        res = requests.post(
            self.endpoint,
            json=payload,
            headers={"x-api-key": self.api_key},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()
