from uaal_sdk.client import UAALClient

action = {
    "agent": "llama-1",
    "do": "create_note",
    "target": {"type": "note", "attributes": {"content": "Remember to buy coffee"}},
    "confidence": 0.85,
}
c = UAALClient("http://127.0.0.1:8000")
print(c.send_action("llama", action))
