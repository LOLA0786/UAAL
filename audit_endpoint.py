from fastapi import APIRouter, Depends, HTTPException
from db import SessionLocal, ActionRecord
import json
import policy_manager

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

@router.get("/action/{action_id}")
def action_audit(action_id: str, current_user = Depends(__import__('middleware_auth').get_current_user)):
    """
    Returns combined audit trail for a single action:
      - stored action record
      - policy evaluations (attached policy flags if any)
      - deliveries / compensator state
    """
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="action not found")
        # Attempt to gather policy history from policy_audit table if it exists
        try:
            audits = db.execute(
                "SELECT timestamp, policy_payload, policy_result FROM policy_audit WHERE action_id = :aid ORDER BY timestamp ASC",
                {"aid": action_id},
            ).fetchall()
            audit_list = []
            for r in audits:
                try:
                    payload = json.loads(r[1]) if r[1] else None
                except Exception:
                    payload = r[1]
                try:
                    result = json.loads(r[2]) if r[2] else None
                except Exception:
                    result = r[2]
                audit_list.append({"timestamp": r[0].isoformat() if hasattr(r[0],'isoformat') else str(r[0]), "policy": payload, "result": result})
        except Exception:
            audit_list = []

        return {
            "action": {
                "action_id": row.action_id,
                "actor_id": row.actor_id,
                "verb": row.verb,
                "parameters": row.parameters,
                "confidence": row.confidence,
                "reasoning": row.reasoning,
                "state": row.state,
                "timestamp": row.timestamp.isoformat() if hasattr(row.timestamp,'isoformat') else str(row.timestamp),
                "deliveries": row.deliveries,
                "org_id": getattr(row, "org_id", None)
            },
            "policy_audit": audit_list,
        }
    finally:
        db.close()
