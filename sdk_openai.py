import requests, json
def send_openai_action(server_url, assistant_id, name, arguments, api_key=None, require_approval=False, user_id=None):
    payload = {
        "adapter": "openai_tools",
        "agent_output": {
            "assistant_id": assistant_id,
            "name": name,
            "arguments": arguments,
            "confidence": arguments.get("confidence", 0.9)
        },
        "require_approval": require_approval,
        "user_id": user_id
    }
    headers = {"Content-Type":"application/json"}
    if api_key: headers["x-api-key"] = api_key
    r = requests.post(f"{server_url.rstrip('/')}/api/v1/actions", json=payload, headers=headers, timeout=5)
    return r.json()
