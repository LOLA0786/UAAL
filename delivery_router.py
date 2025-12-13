from typing import Dict, Any
from effectors.emailer import EmailEffector
from effectors.gcal import GoogleCalendarEffector
from effectors.slacker import SlackEffector
from effectors.webhook import WebhookEffector

ROUTER = {
    "send_email": EmailEffector(),
    "create_calendar_event": GoogleCalendarEffector(),
    "post_slack_message": SlackEffector(),
    "webhook_call": WebhookEffector(),
}


def route_action(verb: str, parameters: Dict[str, Any]):
    effector = ROUTER.get(verb)
    if not effector:
        return {"status": "no_effector"}

    return effector.deliver(parameters)
