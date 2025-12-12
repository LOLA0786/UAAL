from uaal_sdk.client import UAALClient

action = {
    "agent_id": "gemini-test",
    "action": "create_event",
    "entity": {"type": "event", "attributes": {"title": "Gemini event"}},
    "score": 0.9,
}
c = UAALClient("http://127.0.0.1:8000")
print(c.send_action("gemini", action))
