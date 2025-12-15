from celery import Celery
from delivery_router import handle_delivery_result
from retry_backoff import with_retry
from observability import emit_event

app = Celery(
    "uaal_worker",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
)


@app.task(bind=True, autoretry_for=(), retry_backoff=False)
def deliver_action(self, action_id: str):
    try:
        result = handle_delivery_result(action_id)
        emit_event("delivery.success", {"action_id": action_id})
        return result
    except Exception as e:
        emit_event("delivery.error", {"action_id": action_id, "error": str(e)})
        raise
