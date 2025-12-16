from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from datetime import datetime, timedelta
import hashlib, json, time

router = APIRouter(prefix="/agent", tags=["agent"])

# =========================
# ORG STATE (DEMO)
# =========================
ORGS = {
    "acme": {
        "policy": {
            "high_risk_actions": ["execute"],
            "approval_roles": ["admin", "security"],
            "sla_minutes": 2
        }
    }
}

# =========================
# AGENT GRAPH (DEMO)
# =========================
AGENT_GRAPH = {
    "agent-A": ["agent-B", "agent-C"],
    "agent-B": [],
    "agent-C": ["agent-D"],
    "agent-D": []
}

AUDIT_LOG = []
PENDING = {}

# =========================
# MODELS
# =========================
class AgentActionRequest(BaseModel):
    org: str
    agent_id: str
    action: Literal["read", "execute", "simulate", "risk_score"]

class ApprovalDecision(BaseModel):
    role: Literal["admin", "security"]
    decision: Literal["approve", "reject"]

# =========================
# SIGN POLICY
# =========================
def sign_policy(policy: dict):
    payload = json.dumps(policy, sort_keys=True)
    signature = hashlib.sha256(payload.encode()).hexdigest()
    return signature

# =========================
# ACTION
# =========================
@router.post("/action")
def agent_action(req: AgentActionRequest):
    if req.org not in ORGS:
        raise HTTPException(404, "Org not found")

    policy = ORGS[req.org]["policy"]
    trace = hashlib.sha256(f"{req.agent_id}:{req.action}:{time.time()}".encode()).hexdigest()[:8]

    status = "approved"
    reason = None

    if req.action in policy["high_risk_actions"]:
        status = "needs_approval"
        reason = "HIGH_RISK_ACTION"

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "org": req.org,
        "agent": req.agent_id,
        "action": req.action,
        "status": status,
        "reason": reason,
        "trace_id": trace
    }

    AUDIT_LOG.append(entry)

    if status == "needs_approval":
        PENDING[trace] = {
            **entry,
            "expires_at": (datetime.utcnow() + timedelta(minutes=policy["sla_minutes"])).isoformat(),
            "approvals": []
        }

    return entry

# =========================
# APPROVAL
# =========================
@router.post("/approve/{trace_id}")
def approve(trace_id: str, body: ApprovalDecision):
    if trace_id not in PENDING:
        raise HTTPException(404, "Not pending")

    item = PENDING[trace_id]
    item["approvals"].append(body.role)

    if body.decision == "reject":
        item["status"] = "rejected"
        item["reason"] = "HUMAN_REJECTED"
    elif set(item["approvals"]) >= set(ORGS[item["org"]]["policy"]["approval_roles"]):
        item["status"] = "approved"
        item["reason"] = "HUMAN_APPROVED"
    else:
        return item

    AUDIT_LOG.append(item)
    del PENDING[trace_id]
    return item

# =========================
# POLICY BUNDLE
# =========================
@router.get("/policy/{org}")
def get_policy(org: str):
    policy = ORGS[org]["policy"]
    return {
        "org": org,
        "policy": policy,
        "signature": sign_policy(policy)
    }

# =========================
# AGENT GRAPH
# =========================
@router.get("/graph")
def agent_graph():
    return AGENT_GRAPH

# =========================
# SOC-2 MAPPING
# =========================
@router.get("/soc2")
def soc2_controls():
    return {
        "CC6.1": "Role-based access approvals",
        "CC7.2": "Policy enforcement before execution",
        "CC7.3": "Audit logging with immutable trace IDs",
        "CC8.1": "Change management via signed policy bundles"
    }

# =========================
# AUDIT
# =========================
@router.get("/audit")
def audit():
    return AUDIT_LOG[-50:]

# ---- Amount-based risk gate ----
MAX_AUTO_APPROVE_AMOUNT = 5000
