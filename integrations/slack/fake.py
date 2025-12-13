from integrations.base import IntegrationBase


class SlackFake(IntegrationBase):
    def send_message(self, channel: str = "#general", text: str = "", **kwargs):
        print(f"[FAKE SLACK] channel={channel}, text={text}")
        return {"fake": True, "sent": True}

    def undo_send_message(self, **kwargs):
        print("[FAKE SLACK] undo_send_message")
