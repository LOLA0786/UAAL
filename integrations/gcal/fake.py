from integrations.base import IntegrationBase


class GCalFake(IntegrationBase):
    def create_event(self, title: str, start: str = None, **kwargs):
        print(f"[FAKE GCAL] create_event: {title} @ {start}")
        return {"fake": True, "event_created": True}

    def undo_create_event(self, **kwargs):
        print("[FAKE GCAL] undo_create_event")
