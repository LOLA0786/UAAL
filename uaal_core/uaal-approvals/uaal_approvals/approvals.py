import uuid
from datetime import datetime
from .store import save_request, load_request, update_status

def request_approval(decision):
    approval_id = str(uuid.uuid4())

    record = {
        "approval_id": approval_id,
        "decision_id": decision.id,
        "agent": decision.agent,
        "action": decision.action,
        "payload": decision.payload,
        "status": "PENDING",
        "requested_at": datetime.utcnow().isoformat(),
    }

    save_request(record)
    return record

def resolve_approval(approval_id: str, approved: bool, reviewer: str):
    record = load_request(approval_id)
    if not record:
        raise ValueError("Approval not found")

    record["status"] = "APPROVED" if approved else "REJECTED"
    record["reviewer"] = reviewer
    record["resolved_at"] = datetime.utcnow().isoformat()

    update_status(record)
    return record
