from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import json, os, uuid

router = APIRouter(prefix="/admin")

AUDIT_FILE = "audit_log.json"

def load():
    if not os.path.exists(AUDIT_FILE):
        return []
    return json.load(open(AUDIT_FILE))

def save(d):
    json.dump(d, open(AUDIT_FILE,"w"))

class RunRequest(BaseModel):
    agent: str
    action: str

class ApproveRequest(BaseModel):
    trace_id: str
    decision: str

class AuditEvent(BaseModel):
    timestamp: str
    org: str
    agent: str
    action: str
    status: str
    reason: Optional[str]
    trace_id: str

GRAPH: Dict[str, List[str]] = {
    "billing-agent": ["ledger-agent","notification-agent"],
    "ledger-agent": [],
    "notification-agent": ["email-agent"],
    "email-agent": []
}

@router.get("/graph")
def graph():
    return GRAPH

@router.get("/audit")
def audit():
    return load()

@router.get("/metrics")
def metrics():
    a = load()
    return {
        "total_actions": len(a),
        "approved": len([x for x in a if x["status"]=="approved"]),
        "rejected": len([x for x in a if x["status"]=="rejected"]),
        "pending": len([x for x in a if x["status"]=="needs_approval"]),
    }

@router.post("/run")
def run(req: RunRequest):
    audit = load()
    trace = uuid.uuid4().hex[:8]

    status = "approved"
    reason = None
    if req.action == "execute":
        status = "needs_approval"
        reason = "HIGH_RISK_ACTION"

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "org": "acme",
        "agent": req.agent,
        "action": req.action,
        "status": status,
        "reason": reason,
        "trace_id": trace
    }

    audit.append(event)
    save(audit)
    return event

@router.post("/approve")
def approve(req: ApproveRequest):
    audit = load()
    for e in audit:
        if e["trace_id"] == req.trace_id and e["status"]=="needs_approval":
            e["status"] = req.decision
    save(audit)
    return {"ok": True}
