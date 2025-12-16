from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import require_admin
import secrets

router = APIRouter(prefix="/admin", tags=["admin"])

API_KEYS = {}

class CreateAgentRequest(BaseModel):
    owner: str = "demo"
    role: str = "agent"
    name: str | None = None

@router.post("/api-keys/create")
def create_api_key(
    payload: CreateAgentRequest,
    admin=Depends(require_admin)
):
    key = secrets.token_hex(16)

    API_KEYS[key] = {
        "owner": payload.owner,
        "role": payload.role,
        "name": payload.name,
        "active": True
    }

    return {
        "api_key": key,
        "owner": payload.owner,
        "role": payload.role,
        "name": payload.name
    }

@router.get("/audit")
def audit(admin=Depends(require_admin)):
    return {
        "total_keys": len(API_KEYS),
        "keys": API_KEYS
    }

from admin.audit_export import export_audit_csv

@router.get("/audit/export")
def export_audit():
    return export_audit_csv()

from admin.metrics import metrics

@router.get("/metrics")
def pilot_metrics():
    return metrics()
from storage import get_db
from datetime import datetime

@router.post("/approve/{trace_id}")
def approve_action(trace_id: str):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    UPDATE audit
    SET status='approved', reason=NULL
    WHERE trace_id=? AND status='needs_approval'
    """, (trace_id,))

    conn.commit()
    conn.close()

    return {
        "trace_id": trace_id,
        "status": "approved",
        "approved_at": datetime.utcnow().isoformat()
    }
