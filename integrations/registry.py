import os

from integrations.slack.fake import SlackFake
from integrations.slack.real import SlackReal

from integrations.gmail.fake import GmailFake
from integrations.gmail.real import GmailReal

from integrations.gcal.fake import GCalFake
from integrations.gcal.real import GCalReal

from integrations.notion.fake import NotionFake
from integrations.notion.real import NotionReal


MODE = os.getenv("UAAL_MODE", "fake")  # fake | real


INTEGRATIONS = {
    "slack": SlackReal() if MODE == "real" else SlackFake(),
    "gmail": GmailReal() if MODE == "real" else GmailFake(),
    "gcal": GCalReal() if MODE == "real" else GCalFake(),
    "notion": NotionReal() if MODE == "real" else NotionFake(),
}


def get_integration_for(object_type: str):
    """
    Maps UAAL object types to integrations.
    E.g.: verb=create_event, object_type=event → gcal
    """
    mapping = {
        "event": "gcal",
        "message": "slack",
        "email": "gmail",
        "doc": "notion",
        "record": "notion",
    }

    integ_key = mapping.get(object_type, "slack")
    return INTEGRATIONS[integ_key]
