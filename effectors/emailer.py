"""
Simple Email effector stub (SendGrid or SMTP).
Replace send_email() internals with real provider code.
"""
import os
import logging
logger = logging.getLogger("uaal.effectors.emailer")

def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Send email via provider (SendGrid/SMTP).
    Returns dict with status and provider response.
    """
    logger.info("send_email() called: to=%s subject=%s", to_email, subject)
    # TODO: integrate SendGrid / SMTP here
    # Example: sendgrid_client.send(...)
    return {"status": "ok", "provider": "stub", "to": to_email}
