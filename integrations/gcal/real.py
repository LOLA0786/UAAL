from integrations.base import IntegrationBase


class GCalReal(IntegrationBase):
    """
    Placeholder for real Google Calendar OAuth implementation.
    """

    def create_event(self, title: str, start: str = None, **kwargs):
        raise NotImplementedError("Real GCal API requires OAuth2")
