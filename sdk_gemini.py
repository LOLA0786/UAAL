import requests
def send_gemini_action(server_url, agent_id, action, entity, score=0.9, api_key=None, user_id=None):
    payload = {
        "adapter": "gemini",
        "agent_output": {
            "agent_id": agent_id,
            "action": action,
            "entity": entity,
            "score": score
        },
        "user_id": user_id
    }
    headers = {"Content-Type":"application/json"}
    if api_key: headers["x-api-key"] = api_key
    r = requests.post(f"{server_url.rstrip('/')}/api/v1/actions", json=payload, headers=headers, timeout=5)
    return r.json()
