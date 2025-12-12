def publish_action(event: dict):
    print("[KafkaStub] publish_action:", event)
    return {"status": "ok", "stub": True}
