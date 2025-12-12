# Insert the following lines inside receive_action after policy.log_audit(...)
# (this is just a snippet — open app_v2.py and paste here)
import time
start_ts = time.time()
# increment action counter using actor id
actor_id = user_id or ua.get("actor", {}).get("id", "unknown")
observability.ACTION_COUNTER.labels(actor_id=actor_id).inc()
# record policy violations if any
if result.get("flags"):
    observability.POLICY_VIOLATIONS.inc()
# after delivery logic, observe latency:
latency = time.time() - start_ts
observability.ACTION_LATENCY.labels(endpoint="/api/v1/actions").observe(latency)
# update approval queue gauge (rough)
if row.state == "pending":
    observability.APPROVAL_QUEUE_GAUGE.inc()
else:
    try:
        observability.APPROVAL_QUEUE_GAUGE.dec()
    except Exception:
        pass
