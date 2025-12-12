"""
Google Calendar effector stub.
Replace with real google-api-python-client integration.
"""

import logging
logger = logging.getLogger("uaal.effectors.gcal")

def create_event(calendar_id: str, summary: str, start_iso: str, end_iso: str, attendees=None):
    logger.info(
        "create_event() stub: calendar=%s summary=%s start=%s end=%s",
        calendar_id, summary, start_iso, end_iso
    )
    # Placeholder response — simulates event creation
    return {
        "status": "ok",
        "calendar_id": calendar_id,
        "event_id": "evt_stub_12345",
        "summary": summary,
    }
