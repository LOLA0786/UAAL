from db import SessionLocal, ActionRecord
import datetime
import json

def replay_action(action_id, dry_run=True):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            return {"error": "not found"}
        # Simulate re-evaluating policy + show what would happen
        action_dict = {
            "action_id": row.action_id,
            "actor": {"id": row.actor_id, "type": row.actor_type},
            "verb": row.verb,
            "object": {"type": row.object_type, "id": row.object_id},
            "parameters": row.parameters,
            "confidence": row.confidence,
            "reasoning": row.reasoning
        }
        # For a dry run, return policy evaluation outcome
        return {"dry_run": dry_run, "action": action_dict}
    finally:
        db.close()
