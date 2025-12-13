from typing import Dict, Any
from .base import Effector


class EmailEffector(Effector):
    """Simple mock email sender."""

    def deliver(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        to = payload.get("to")
        subject = payload.get("subject")
        body = payload.get("body")

        # In real world: integrate SMTP / SendGrid / SES
        print(f"[EMAIL] Sending to={to} subject={subject}")
        return {"status": "sent", "to": to, "subject": subject}
