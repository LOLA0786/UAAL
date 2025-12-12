"""
Simple shim to support dry-run replay of an action without side-effects.
It reads action from DB and returns a simulation result.
"""
from db import SessionLocal, ActionRecord

def replay_action(action_id: str, dry_run: bool = True):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            return {"status":"not_found"}
        # Simulate execution path: return what would be called
        return {
            "action_id": action_id,
            "simulate": True,
            "verb": row.verb,
            "parameters": row.parameters,
            "would_call": "effectors" if row.verb in ("create_event","send_email") else "webhook"
        }
    finally:
        db.close()
