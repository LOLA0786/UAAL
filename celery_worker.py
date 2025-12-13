from celery import Celery
from delivery_router import route_action
from delivery.middleware import handle_delivery_result

app = Celery(
    "uaal_worker",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
)


@app.task(name="deliver_action", bind=True)
def deliver_action(self, action_id: str, verb: str, parameters: dict):
    try:
        result = route_action(verb, parameters)
    except Exception as e:
        result = {"status": "error", "error": str(e)}

    # attempt count comes from Celery retries
    attempt = self.request.retries
    handle_delivery_result(action_id, result, attempt)

    if result.get("status") == "error":
        raise self.retry(exc=Exception(result["error"]), countdown=2)

    return result
