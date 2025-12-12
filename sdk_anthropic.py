import requests
def send_anthropic_action(server_url, assistant_id, intent, target, confidence=0.9, api_key=None, user_id=None):
    payload = {
        "adapter": "anthropic",
        "agent_output": {
            "assistant_id": assistant_id,
            "intent": intent,
            "target": target,
            "confidence": confidence
        },
        "user_id": user_id
    }
    headers = {"Content-Type":"application/json"}
    if api_key: headers["x-api-key"] = api_key
    r = requests.post(f"{server_url.rstrip('/')}/api/v1/actions", json=payload, headers=headers, timeout=5)
    return r.json()
