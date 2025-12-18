import requests
from datetime import datetime
import uuid

CONTROL = "http://127.0.0.1:8000/admin"

def emit(action, status, reason=None):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "org": "acme",
        "agent": "billing-agent",
        "action": action,
        "status": status,
        "reason": reason,
        "trace_id": TRACE_ID
    }
    requests.post(f"{CONTROL}/audit/log", json=payload)

TRACE_ID = uuid.uuid4().hex[:8]

emit("read", "approved")
emit("simulate", "approved")
emit("execute", "needs_approval", "HIGH_RISK_ACTION")

print("Billing agent finished (audit emitted)")
