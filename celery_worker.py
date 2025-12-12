from celery import Celery
import os, logging
from db import SessionLocal, ActionRecord
from effectors.emailer import send_email
from effectors.gcal import create_event
from effectors.compensator import register_compensator
import observability, retry_backoff, analytics, events.kafka_producer as kafka_producer

CELERY_BROKER = os.environ.get("CELERY_BROKER", "redis://localhost:6379/1")
CELERY_BACKEND = os.environ.get("CELERY_BACKEND", "redis://localhost:6379/2")
app = Celery("celery_worker", broker=CELERY_BROKER, backend=CELERY_BACKEND)
logger = logging.getLogger("uaal.celery")

# Example task with retries and backoff
@app.task(bind=True, max_retries=5, autoretry_for=(Exception,), retry_backoff=True)
def deliver_action(self, action_id):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            return {"status": "not_found"}
        logger.info("Delivering action %s verb=%s", action_id, row.verb)
        # instrument
        observability.ACTION_COUNTER.labels(actor_id=row.actor_id).inc()
        start = None
        try:
            # example verb handling
            if row.verb in ("create_calendar_event", "create_event"):
                start = __import__('time').time()
                r = create_event(calendar_id=row.parameters.get("calendar_id", "primary"),
                                 summary=row.parameters.get("title", "UAAL event"),
                                 start_iso=row.parameters.get("start"),
                                 end_iso=row.parameters.get("end"))
                # register compensator to delete event if provider returns id
                if r and r.get("event_id"):
                    register_compensator(row.action_id, lambda eid: {"deleted": eid}, r.get("event_id"))
                deliveries = [{"provider": "gcal", "result": r}]
            elif row.verb in ("send_email",):
                r = send_email(to_email=row.parameters.get("to"), subject=row.parameters.get("subject","UAAL"), body=row.parameters.get("body",""))
                deliveries = [{"provider":"email", "result": r}]
            else:
                # generic webhook delivery (if configured)
                deliveries = []
            # mark delivered
            row.delivered = True
            row.deliveries = deliveries
            row.state = "delivered"
            db.commit()
            # publish event to kafka
            try:
                kafka_producer.publish_action({"action_id": action_id, "actor": row.actor_id, "verb": row.verb})
            except Exception:
                pass
            # latency observe
            if start:
                observability.ACTION_LATENCY.labels(endpoint="/api/v1/actions").observe(__import__('time').time() - start)
            return {"status": "delivered", "deliveries": deliveries}
        except Exception as exc:
            # log and push to retry queue for visibility
            retry_backoff.push_retry({"action_id": action_id, "error": str(exc)}, attempt=1)
            logger.exception("Delivery failed, retrying: %s", exc)
            raise self.retry(exc=exc)
    finally:
        db.close()
