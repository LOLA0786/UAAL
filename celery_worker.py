from celery import Celery
import os
import json
from db import SessionLocal, ActionRecord
import requests
from effectors import emailer, gcal, compensator
from retry import push_retry

CELERY_BROKER = os.environ.get("CELERY_BROKER", "redis://localhost:6379/1")
CELERY_BACKEND = os.environ.get("CELERY_BACKEND", "redis://localhost:6379/2")

app = Celery("uaal_worker", broker=CELERY_BROKER, backend=CELERY_BACKEND)

@app.task(bind=True, max_retries=5, autoretry_for=(Exception,), retry_backoff=True)
def deliver_action(self, action_id):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            return {"status": "not_found"}
        # Simulated delivery: call webhooks/effectors
        # Example: if verb == create_calendar_event -> call gcal.create_event
        payload = row.parameters or {}
        try:
            if row.verb in ("create_calendar_event", "create_event"):
                r = gcal.create_event(calendar_id=payload.get("calendar_id", "primary"),
                                      summary=payload.get("title", "UAAL event"),
                                      start_iso=payload.get("start"),
                                      end_iso=payload.get("end"))
                # Register compensator to delete event if needed
                compensator.register_compensator(row.action_id, lambda eid: {"deleted": eid}, r.get("event_id"))
            # Mark as delivered
            row.delivered = True
            db.commit()
            return {"status": "delivered", "deliveries": [r]}
        except Exception as exc:
            # push to retry sorted set with backoff
            push_retry({"action_id": action_id, "error": str(exc)}, attempt=1)
            raise
    finally:
        db.close()
