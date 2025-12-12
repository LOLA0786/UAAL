from uaal_sdk.client import UAALClient

action = {
    "assistant_id": "claude-bot",
    "intent": "create_calendar_event",
    "target": {
        "type": "event",
        "attributes": {"title": "Lunch", "start": "2026-01-06T12:00:00Z"},
    },
    "confidence": 0.92,
}
c = UAALClient("http://127.0.0.1:8000")
print(c.send_action("anthropic", action))
