from uaal_sdk.client import UAALClient

action = {
    "assistant_id": "example-bot",
    "name": "create_event",
    "arguments": {
        "object_type": "event",
        "title": "Meet with team",
        "start": "2026-01-05T10:00:00Z",
    },
    "confidence": 0.95,
}
c = UAALClient("http://127.0.0.1:8000")
print(c.send_action("openai_tools", action))
