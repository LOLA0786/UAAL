from uaal_sdk.client import UAALClient

action = {
    "assistant_id": "noisy-bot",
    "intent": "delete_resource",
    "target": {"type": "resource", "attributes": {"id": "r1"}},
    "confidence": 0.2,
}
c = UAALClient("http://127.0.0.1:8000")
print(c.send_action("openai_assistant", action))
