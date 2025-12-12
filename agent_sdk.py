import requests


def send_to_uaal(server_url, adapter, agent_output, require_approval=False):
    payload = {
        "adapter": adapter,
        "agent_output": agent_output,
        "require_approval": require_approval,
    }
    resp = requests.post(f"{server_url}/api/v1/actions", json=payload, timeout=10)
    return resp.json()
