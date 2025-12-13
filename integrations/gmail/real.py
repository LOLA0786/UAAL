from integrations.base import IntegrationBase


class GmailReal(IntegrationBase):
    """
    Placeholder for Gmail OAuth2 integration.
    In Phase 5-6, we add:
      - token refresh
      - send email via SMTP / Gmail API
    """

    def send_message(self, to: str, subject: str, body: str, **kwargs):
        raise NotImplementedError("Gmail real mode requires OAuth setup")
