import uuid
import time

class Trace:
    def __init__(self, action_id):
        self.trace_id = str(uuid.uuid4())
        self.action_id = action_id
        self.spans = []

    def span(self, name):
        self.spans.append({
            "name": name,
            "ts": time.time()
        })
