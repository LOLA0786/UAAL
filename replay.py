"""Replay / simulation helpers."""
from db import SessionLocal, ActionRecord
from typing import Dict, Any


def replay_action(action_id: str, dry_run: bool = True) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            return {"error": "not found"}
        action = {
            "action_id": row.action_id,
            "actor": {"id": row.actor_id, "type": row.actor_type},
            "verb": row.verb,
            "object": {"type": row.object_type, "id": row.object_id},
            "parameters": row.parameters,
            "confidence": row.confidence,
            "reasoning": row.reasoning,
        }
        # In a dry run we only run policy evaluation; in real replay we'd attempt delivery in sandbox.
        return {"dry_run": dry_run, "action": action}
    finally:
        db.close()
