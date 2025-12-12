"""Tiny SDK helper for agents to send OpenAI-like actions to UAAL."""
import requests
from typing import Any, Dict, Optional


def send_openai_action(
    server_url: str,
    assistant_id: str,
    name: str,
    arguments: Dict[str, Any],
    api_key: Optional[str] = None,
    require_approval: bool = False,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "adapter": "openai_tools",
        "agent_output": {
            "assistant_id": assistant_id,
            "name": name,
            "arguments": arguments,
            "confidence": arguments.get("confidence", 0.9),
        },
        "require_approval": require_approval,
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
