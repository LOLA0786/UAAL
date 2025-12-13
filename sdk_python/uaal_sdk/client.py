import time
import requests
from typing import Dict, Any, Optional
from .models import ActionResult, ActionRequest


class UAALClient:
    def __init__(self, api_key: str, base_url: str = "http://127.0.0.1:8000"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def submit_action(
        self, verb: str, object_type: str, parameters: Dict[str, Any]
    ) -> ActionResult:

        payload = {
            "adapter": "sdk_raw",
            "payload": {
                "verb": verb,
                "parameters": parameters,
                "object_type": object_type,
                "confidence": 0.95,
                "reasoning": "UAAL Python SDK",
            },
        }

        r = requests.post(
            f"{self.base_url}/api/v1/actions",
            json=payload,
            headers=self._headers(),
            timeout=10,
        )

        r.raise_for_status()
        return ActionResult(**r.json())

    # retry wrapper
    def retry_submit(
        self, verb: str, object_type: str, parameters: Dict[str, Any],
        retries: int = 3, delay: float = 1.0
    ) -> ActionResult:
        for i in range(retries):
            try:
                return self.submit_action(verb, object_type, parameters)
            except Exception as e:
                if i == retries - 1:
                    raise e
                time.sleep(delay)
                delay *= 2  # exponential backoff
