from integrations.base import IntegrationBase


class GmailFake(IntegrationBase):
    def send_message(self, to: str, subject: str, body: str, **kwargs):
        print(f"[FAKE GMAIL] to={to} subject={subject} body={body}")
        return {"fake": True, "sent": True}

    def undo_send_message(self, **kwargs):
        print("[FAKE GMAIL] undo_send_message")
