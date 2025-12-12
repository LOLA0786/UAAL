"""Tiny SDK helper for Anthropic-style agents."""
import requests
from typing import Any, Dict, Optional


def send_anthropic_action(
    server_url: str,
    assistant_id: str,
    intent: str,
    target: Dict[str, Any],
    confidence: float = 0.9,
    api_key: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "adapter": "anthropic",
        "agent_output": {
            "assistant_id": assistant_id,
            "intent": intent,
            "target": target,
            "confidence": confidence,
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
