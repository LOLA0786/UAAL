import time
import uuid

EVENTS = []

def emit(event_type, payload):
    EVENTS.append({
        "id": str(uuid.uuid4()),
        "type": event_type,
        "payload": payload,
        "ts": time.time(),
    })

def stats():
    by_type = {}
    for e in EVENTS:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    return by_type
