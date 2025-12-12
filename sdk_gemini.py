"""Tiny SDK helper for Gemini-style agents."""
import requests
from typing import Any, Dict, Optional


def send_gemini_action(
    server_url: str,
    agent_id: str,
    action: str,
    entity: Dict[str, Any],
    score: float = 0.9,
    api_key: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "adapter": "gemini",
        "agent_output": {
            "agent_id": agent_id,
            "action": action,
            "entity": entity,
            "score": score,
        },
        "user_id": user_id,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    resp = requests.post(
        f"{server_url.rstrip('/')}/api/v1/actions",
        json=payload,
        headers=headers,
        timeout=10,
    )
    return resp.json()
